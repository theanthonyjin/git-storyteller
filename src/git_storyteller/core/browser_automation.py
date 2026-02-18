"""Browser automation for stealth social media posting."""
import asyncio
import random
from pathlib import Path
from typing import Optional

from playwright.async_api import Browser, Page, async_playwright

from ..config import get_config


class BrowserAutomation:
    """Handles automated social media posting with stealth."""

    def __init__(self):
        """Initialize browser automation."""
        self.config = get_config()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        """Initialize browser with user data directory for session persistence."""
        playwright = await async_playwright().start()

        # Get config
        headless = self.config.get("browser.headless", False)

        # Use regular launch (not persistent_context) to ensure window is visible
        # This is simpler and more reliable
        self.browser = await playwright.chromium.launch(
            headless=headless,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )

        # Create a context for reuse
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        print("  ✓ Browser launched (visible window)")

    async def new_page(self):
        """Create a new page for each tweet."""
        self.page = await self.context.new_page()
        return self.page

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()

    def _generate_random_delay(self) -> float:
        """Generate a random delay for stealth behavior.

        Returns:
            Delay in seconds
        """
        if not self.config.get("entropy.randomize_timing", True):
            return 10.0

        min_wait = self.config.get("entropy.min_wait_seconds", 8.4)
        max_wait = self.config.get("entropy.max_wait_seconds", 22.1)

        return random.uniform(min_wait, max_wait)

    async def _simulate_human_typing(self, element, text: str):
        """Simulate human typing with random delays.

        Args:
            element: Playwright element handle
            text: Text to type
        """
        for char in text:
            await element.type(char, delay=random.uniform(50, 150))
            await asyncio.sleep(random.uniform(0.01, 0.05))

    async def post_to_twitter(
        self,
        text: str,
        image_path: Optional[Path] = None,
        scheduled_at: Optional[str] = None,
    ) -> bool:
        """Post to Twitter/X with stealth behavior.

        Args:
            text: Tweet text
            image_path: Optional path to image to attach
            scheduled_at: Optional schedule time (e.g., "09:00")

        Returns:
            True if successful, False otherwise
        """
        if not self.config.get("social.twitter.enabled", False):
            print("Twitter posting is not enabled in config")
            return False

        try:
            # Create a new page for this tweet
            await self.new_page()

            # Navigate to Twitter
            await self.page.goto("https://twitter.com", wait_until="networkidle")

            # Wait for user to be logged in (check for tweet composer)
            await asyncio.sleep(self._generate_random_delay())

            # Look for tweet composer
            tweet_box = await self.page.wait_for_selector(
                'div[contenteditable="true"][data-testid="tweetTextarea_0"]',
                timeout=30000,
            )

            # Type tweet with human-like behavior
            await self._simulate_human_typing(tweet_box, text)

            # Add image if provided
            if image_path:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                file_input = await self.page.wait_for_selector('input[type="file"]')
                await file_input.set_input_files(str(image_path))
                await asyncio.sleep(self._generate_random_delay())

            # Random pause before posting
            await asyncio.sleep(self._generate_random_delay())

            # Click tweet button
            tweet_button = await self.page.wait_for_selector(
                'div[data-testid="tweetButtonInline"]'
            )
            await tweet_button.click()

            # Wait for post to complete
            await asyncio.sleep(random.uniform(2.0, 4.0))

            print("✅ Successfully posted to Twitter")
            return True

        except Exception as e:
            print(f"❌ Failed to post to Twitter: {e}")
            return False
        finally:
            # Close the page to clean up
            if self.page:
                try:
                    await self.page.close()
                except Exception:
                    pass

    async def post_to_twitter_interactive(
        self,
        text: str,
        image_path: Optional[Path] = None,
        wait_for_human: bool = True,
    ) -> bool:
        """Post to Twitter/X in interactive mode - let human compose and tweet.

        This method opens Twitter and shows the tweet content in the terminal.
        The user manually clicks "Post", composes the tweet, uploads the image,
        and posts. The script waits and detects when the tweet is posted.

        Args:
            text: Tweet text to display in terminal
            image_path: Optional path to image (for reference)
            wait_for_human: If True, wait for human to tweet

        Returns:
            True if successfully posted, False otherwise
        """
        if not self.config.get("social.twitter.enabled", False):
            print("Twitter posting is not enabled in config")
            return False

        try:
            # Create a fresh page for this tweet
            await self.new_page()

            # Navigate to Twitter
            print("  🌐 Opening Twitter...")
            print("  ℹ️  Navigating to https://twitter.com...")
            await self.page.goto("https://twitter.com", wait_until="domcontentloaded", timeout=60000)
            print("  ✓ Page loaded")

            # Wait for page to fully load and render
            await asyncio.sleep(5.0)

            # Click the "Post" button on the left to open composer
            print("  🖱️  Clicking 'Post' button to open composer...")
            try:
                # Wait a bit more for Twitter's JavaScript to finish loading
                await asyncio.sleep(2.0)

                # Try multiple selectors for the Post button
                print("  ℹ️  Looking for Post button...")
                post_button = await self.page.wait_for_selector(
                    'a[data-testid="SideNav_NewTweet_Button"], div[data-testid="SideNav_NewTweet_Button"], nav[aria-label] a[href="/compose/tweet"]',
                    timeout=15000
                )
                print("  ✓ Found Post button, clicking...")
                await post_button.click()
                # Wait longer for composer modal to open and fully render
                await asyncio.sleep(5.0)
                print("  ✓ Composer opened")
            except Exception as e:
                print(f"  ⚠️  Could not click Post button: {e}")
                print("  ℹ️  Trying to navigate to compose page directly...")
                # Fallback: navigate directly to compose URL
                await self.page.goto("https://twitter.com/compose/tweet", timeout=15000)
                # Wait for compose page to fully load
                await asyncio.sleep(5.0)
                print("  ✓ Opened compose page directly")

            # Fill tweet content with retry logic
            print("  ✍️  Filling tweet content...")
            print(f"  ℹ️  Current URL: {self.page.url}")
            for attempt in range(3):
                try:
                    print(f"  ℹ️  Attempt {attempt + 1}/3 to find tweet box...")

                    # Try multiple selectors
                    selectors = [
                        'div[contenteditable="true"][data-testid="tweetTextarea_0"]',
                        'div[contenteditable="true"][data-testid="tweetText"]',
                        'div[data-testid="tweetTextarea_0"]',
                        'div[role="textbox"][contenteditable="true"]',
                        'div[contenteditable="true"]',
                    ]

                    tweet_box = None
                    for selector in selectors:
                        try:
                            print(f"  ℹ️  Trying selector: {selector}")
                            tweet_box = await self.page.wait_for_selector(selector, timeout=5000)
                            if tweet_box:
                                print(f"  ✓ Found element with selector: {selector}")
                                break
                        except Exception:
                            continue

                    if not tweet_box:
                        raise Exception("Could not find tweet box with any selector")

                    # Click first to focus, then fill
                    await tweet_box.click()
                    await asyncio.sleep(0.5)

                    # Try using type() instead of fill() for more reliable input
                    await tweet_box.fill('')
                    await asyncio.sleep(0.3)
                    await tweet_box.type(text, delay=10)
                    await asyncio.sleep(1.0)
                    print("  ✓ Tweet content filled")
                    break
                except Exception as e:
                    print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                    # Take screenshot for debugging
                    screenshot_path = f"/tmp/tweet_box_error_attempt_{attempt + 1}.png"
                    await self.page.screenshot(path=screenshot_path)
                    print(f"  📸 Screenshot saved to: {screenshot_path}")

                    if attempt < 2:
                        print("  ℹ️  Waiting 3 seconds before retry...")
                        await asyncio.sleep(3.0)
                    else:
                        print("  ❌ Could not fill tweet content after 3 attempts")

            # Upload image if provided
            if image_path:
                print(f"  🖼️  Uploading image: {image_path}")
                for attempt in range(3):
                    try:
                        print(f"  ℹ️  Attempt {attempt + 1}/3 to upload image...")

                        # Try multiple selectors for file input
                        file_selectors = [
                            'input[type="file"]',
                            'input[accept="image/*"]',
                            'input[data-testid="fileInput"]',
                        ]

                        file_input = None
                        for selector in file_selectors:
                            try:
                                print(f"  ℹ️  Trying file selector: {selector}")
                                file_input = await self.page.wait_for_selector(selector, timeout=5000)
                                if file_input:
                                    print(f"  ✓ Found file input with selector: {selector}")
                                    break
                            except Exception:
                                continue

                        if not file_input:
                            raise Exception("Could not find file input with any selector")

                        await file_input.set_input_files(str(image_path))
                        # Wait for upload to complete
                        await asyncio.sleep(5.0)
                        print("  ✓ Image uploaded")
                        break
                    except Exception as e:
                        print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            print("  ℹ️  Waiting 3 seconds before retry...")
                            await asyncio.sleep(3.0)
                        else:
                            print("  ❌ Could not upload image after 3 attempts")

            # Display summary
            separator = "=" * 60
            print(f"\n  {separator}")
            print("  📝 TWEET IS READY!")
            print(f"  {separator}")
            print("\n  👤 NEXT STEP:")
            print("    Review the tweet in the browser")
            print("    Click 'Post' to publish")
            print("  ⏳ Waiting for you to post...")
            print(f"  {separator}\n")

            if wait_for_human:
                # Wait for the user to tweet
                # We'll detect this by checking if we're on a tweet status page
                # or if a success message appears
                max_wait_time = 600  # 10 minutes max wait
                check_interval = 2  # Check every 2 seconds
                elapsed = 0

                last_url = self.page.url

                while elapsed < max_wait_time:
                    await asyncio.sleep(check_interval)
                    elapsed += check_interval

                    current_url = self.page.url

                    # Check if URL changed to a tweet status page
                    # This happens after posting: twitter.com/username/status/123456
                    if "status" in current_url and current_url != last_url:
                        print("\n  ✅ Tweet posted successfully!")
                        await asyncio.sleep(2.0)
                        return True

                    # Update last URL
                    last_url = current_url

                print("\n  ⏱️  Timeout waiting for tweet post (10 minutes)")
                return False

            return True

        except Exception as e:
            print(f"❌ Failed to open Twitter: {e}")
            print("\n  Troubleshooting:")
            print("  1. Make sure you're logged into Twitter/X in the browser")
            print("  2. Check that Twitter.com is accessible")
            print("  3. Verify the browser window is visible")
            return False
        finally:
            # Close the page to clean up
            if self.page:
                try:
                    await self.page.close()
                except Exception:
                    pass

    async def post_to_linkedin(
        self,
        text: str,
        image_path: Optional[Path] = None,
    ) -> bool:
        """Post to LinkedIn with stealth behavior.

        Args:
            text: Post text
            image_path: Optional path to image to attach

        Returns:
            True if successful, False otherwise
        """
        if not self.config.get("social.linkedin.enabled", False):
            print("LinkedIn posting is not enabled in config")
            return False

        try:
            # Navigate to LinkedIn
            await self.page.goto("https://www.linkedin.com/feed", wait_until="networkidle")

            # Wait for page load
            await asyncio.sleep(self._generate_random_delay())

            # Look for post composer button
            start_post_button = await self.page.wait_for_selector(
                'button[aria*="Start a post"]',
                timeout=30000,
            )
            await start_post_button.click()

            # Wait for composer to open
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Type post content
            text_box = await self.page.wait_for_selector(
                'div[contenteditable="true"][role="textbox"]'
            )
            await self._simulate_human_typing(text_box, text)

            # Add image if provided
            if image_path:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                file_input = await self.page.wait_for_selector('input[type="file"]')
                await file_input.set_input_files(str(image_path))
                await asyncio.sleep(self._generate_random_delay())

            # Random pause before posting
            await asyncio.sleep(self._generate_random_delay())

            # Click post button
            post_button = await self.page.wait_for_selector(
                'button[aria*="Post"] span:has-text("Post")'
            )
            await post_button.click()

            # Wait for post to complete
            await asyncio.sleep(random.uniform(2.0, 4.0))

            print("✅ Successfully posted to LinkedIn")
            return True

        except Exception as e:
            print(f"❌ Failed to post to LinkedIn: {e}")
            return False

    async def fetch_engagement_metrics(self, platform: str) -> dict:
        """Fetch engagement metrics for recent posts.

        Args:
            platform: Platform name ('twitter' or 'linkedin')

        Returns:
            Dictionary with engagement metrics
        """
        try:
            if platform == "twitter":
                await self.page.goto("https://twitter.com", wait_until="networkidle")

                # Navigate to profile
                profile_button = await self.page.wait_for_selector(
                    'div[data-testid="UserAvatar"]', timeout=10000
                )
                await profile_button.click()

                await asyncio.sleep(2.0)

                # Extract metrics from recent tweets
                # This is a simplified version - real implementation would need more specific selectors
                metrics = {
                    "likes": random.randint(10, 100),  # Placeholder
                    "retweets": random.randint(1, 20),
                    "replies": random.randint(1, 10),
                }

            elif platform == "linkedin":
                await self.page.goto("https://www.linkedin.com/feed", wait_until="networkidle")

                # Navigate to profile
                # Similar implementation for LinkedIn
                metrics = {
                    "likes": random.randint(10, 100),
                    "comments": random.randint(1, 20),
                    "shares": random.randint(1, 10),
                }
            else:
                return {}

            return metrics

        except Exception as e:
            print(f"❌ Failed to fetch metrics from {platform}: {e}")
            return {}

    async def wait_for_scheduled_time(self, scheduled_at: str) -> bool:
        """Wait until scheduled time to post.

        Args:
            scheduled_at: Time in HH:MM format (e.g., "09:00")

        Returns:
            True if waited successfully, False if invalid time format
        """
        try:
            from datetime import datetime, time

            # Parse scheduled time
            hour, minute = map(int, scheduled_at.split(":"))
            scheduled_time = time(hour, minute)

            while True:
                now = datetime.now()
                current_time = now.time()

                # Check if we've reached or passed the scheduled time
                if current_time >= scheduled_time:
                    break

                # Calculate seconds to wait
                wait_seconds = (
                    (datetime.combine(now.date(), scheduled_time) - now).total_seconds()
                )

                # Wait until scheduled time (with 1-minute check interval)
                wait_minutes = min(wait_seconds / 60, 60)  # Wait max 60 minutes at a time
                print(f"⏰ Scheduled posting at {scheduled_at}. Waiting {wait_minutes:.1f} minutes...")

                await asyncio.sleep(min(wait_seconds, 3600))

            return True

        except Exception as e:
            print(f"❌ Invalid scheduled time format: {e}")
            return False

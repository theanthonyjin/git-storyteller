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

        # Get user data directory from config or use default
        user_data_dir = self.config.get("browser.user_data_dir")
        headless = self.config.get("browser.headless", False)

        # Launch Chrome with user data directory for session persistence
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            channel="chrome",  # Use Chrome instead of Chromium
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,800",
            ],
        )

        # Get or create page
        if len(self.browser.pages) > 0:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()

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

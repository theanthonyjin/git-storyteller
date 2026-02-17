#!/usr/bin/env python3
"""Git-Storyteller: Analyze repositories and post to Twitter.

Usage:
    python analyze_and_tweet.py                    # Watch list mode (default)
    python analyze_and_tweet.py --single            # Single repo mode
    python analyze_and_tweet.py --single --test    # Test mode (preview only)
    python analyze_and_tweet.py --confirm          # Confirm mode (wait for human to tweet)
"""
import argparse
import asyncio
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from git_storyteller.core.git_analyzer import GitAnalyzer
from git_storyteller.core.visual_engine import VisualEngine
from git_storyteller.core.browser_automation import BrowserAutomation
import git


# Paths
WATCH_LIST_PATH = Path(__file__).parent.parent / "config" / "watch_list.yaml"
HISTORY_DIR = Path(__file__).parent.parent / "output" / "e2e_history"
HISTORY_FILE = HISTORY_DIR / "watch_list_history.json"

# Hardcoded watch list for when yaml is not available
SIMPLE_WATCH_LIST = {
    'watched_repos': [
        {
            'name': 'git-storyteller',
            'url': 'https://github.com/theanthonyjin/git-storyteller',
            'enabled': True
        },
        {
            'name': 'cline',
            'url': 'https://github.com/cline/cline',
            'enabled': True
        }
    ]
}


def load_watch_list() -> dict:
    """Load the watch list configuration."""
    if HAS_YAML and WATCH_LIST_PATH.exists():
        with open(WATCH_LIST_PATH) as f:
            return yaml.safe_load(f)
    return SIMPLE_WATCH_LIST


def load_history() -> dict:
    """Load existing commit history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_history(history: dict):
    """Save commit history to file."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def is_first_tweet(history: dict, repo_name: str) -> bool:
    """Check if this is the first tweet for a repo."""
    if repo_name not in history:
        return True
    return not history[repo_name].get('tweets_sent', 0)


def should_skip_tweet(history: dict, repo_name: str, latest_commit_hash: str) -> bool:
    """Check if tweet should be skipped (no new commits)."""
    if is_first_tweet(history, repo_name):
        return False  # Never skip first tweet

    last_tweeted = history[repo_name].get('last_tweeted_commit')
    if last_tweeted == latest_commit_hash:
        return True  # Skip if same commit as last tweet

    return False


def record_tweet_sent(history: dict, repo_name: str, commit_hash: str):
    """Record that a tweet was sent for a repo."""
    if repo_name not in history:
        history[repo_name] = {}

    if 'tweets_sent' not in history[repo_name]:
        history[repo_name]['tweets_sent'] = 0

    history[repo_name]['tweets_sent'] += 1
    history[repo_name]['last_tweeted_commit'] = commit_hash
    history[repo_name]['last_tweeted_at'] = datetime.now().isoformat()


async def process_single_repo(repo_config: dict, mode: str, history: dict, repo_index: int, total_repos: int, browser=None) -> bool:
    """Process a single repository: analyze, generate content, and optionally post.

    Args:
        repo_config: Repository configuration from watch list
        mode: Execution mode ('test', 'auto', or 'confirm')
        history: Commit history dictionary
        repo_index: Index of this repo in the list (for display)
        total_repos: Total number of repos (for display)
        browser: Optional BrowserAutomation instance to reuse

    Returns:
        True if successful, False otherwise
    """
    repo_name = repo_config['name']
    repo_url = repo_config['url']

    print(f"\n{'='*60}")
    print(f"[{repo_index}/{total_repos}] Processing: {repo_name}")
    print(f"{'='*60}")
    print(f"URL: {repo_url}")

    # Check if should skip
    analyzer = GitAnalyzer()

    try:
        # Analyze repository
        print(f"\n[1/4] Analyzing repository...")
        impact = analyzer.analyze(repo_url, is_remote=True)

        if not impact.recent_changes:
            print("  ⚠️  No commits found")
            return False

        latest_commit = impact.recent_changes[0]
        commit_hash = latest_commit.hash

        # Check if we should skip this tweet
        if should_skip_tweet(history, repo_name, commit_hash):
            print(f"  ⏭️  Skipped: No new commits since last tweet")
            print(f"     Last tweeted: {history[repo_name].get('last_tweeted_commit')}")
            print(f"     Current: {commit_hash}")
            return True  # Not a failure, just skipped

        print(f"  ✓ Latest commit: {commit_hash} by {latest_commit.author}")
        print(f"  ✓ Message: {latest_commit.message[:60]}...")

    except Exception as e:
        print(f"  ✗ Failed to analyze: {e}")
        return False

    # Generate visual asset
    print(f"\n[2/4] Generating visual asset...")
    visual_engine = VisualEngine()

    # Extract username/repo from URL for display
    repo_display = repo_name  # Use the repo_name from config
    if "github.com/" in repo_url:
        parts = repo_url.split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            username = parts[0]
            repo_name_clean = parts[1].replace(".git", "")
            repo_display = f"{username}/{repo_name_clean}"

    visual_data = {
        "data": {
            "repo_name": repo_display,
            "description": impact.description or "Open source project",
            "total_commits": impact.total_commits,
            "recent_count": len(impact.recent_changes),
            "marketing_hooks": impact.marketing_hooks,
            "visual_highlights": impact.visual_highlights,
        }
    }

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        image_path = Path(f.name)

    try:
        screenshot = await visual_engine.render_template(
            template_name="bento_metrics",
            data=visual_data,
            commit_hash=commit_hash,
            output_path=image_path,
        )
        print(f"  ✓ Visual generated: {image_path}")
        print(f"  ✓ Image size: {len(screenshot)} bytes")
    except Exception as e:
        print(f"  ✗ Failed to generate visual: {e}")
        image_path = None

    # Generate tweet content
    print(f"\n[3/4] Crafting tweet content...")
    tweet = analyzer.generate_sexy_tweet_content(impact, repo_url=repo_url)

    print(f"  ✓ Tweet length: {len(tweet)} characters")
    print(f"\n  Tweet preview:")
    print("  " + "─" * 50)
    for line in tweet.split("\n"):
        print(f"  {line}")
    print("  " + "─" * 50)

    # Save files
    output_dir = Path(__file__).parent.parent / "output" / repo_name
    output_dir.mkdir(parents=True, exist_ok=True)

    final_image_path = None
    if image_path and image_path.exists():
        final_image_path = output_dir / "tweet_visual.png"
        import shutil
        shutil.copy(image_path, final_image_path)
        print(f"\n  💾 Image saved to: {final_image_path}")

    tweet_file = output_dir / "tweet_content.txt"
    with open(tweet_file, "w") as f:
        f.write(tweet)
    print(f"  💾 Tweet text saved to: {tweet_file}")

    # Test mode - skip posting
    if mode == 'test':
        print(f"\n[4/4] TEST MODE - Skipping Twitter posting")
        print(f"  ℹ️  To actually post, use --confirm or run without flags")
        return True

    # Post to Twitter
    print(f"\n[4/4] Posting to Twitter...")

    if mode == 'confirm':
        print(f"  👤 CONFIRM MODE: Opening browser for human to tweet")
        print(f"  ⚠️  Browser will open with tweet pre-filled")
        print(f"  ⚠️  Review and tweet, then close the browser to continue")
        print(f"  ⏳ Waiting for you to complete the tweet...")

    try:
        # Initialize browser if not provided
        should_close_browser = False
        if browser is None:
            browser = BrowserAutomation()
            await browser.initialize()
            should_close_browser = True

        if mode == 'confirm':
            # In confirm mode, open browser and wait for human to tweet
            # The browser automation fills everything but waits for human to click "Post"
            success = await browser.post_to_twitter_interactive(
                text=tweet,
                image_path=final_image_path if final_image_path else image_path,
                wait_for_human=True
            )
        else:
            # Auto mode - posts automatically
            success = await browser.post_to_twitter(
                text=tweet,
                image_path=final_image_path if final_image_path else image_path,
            )

        if success:
            print(f"  ✓ Successfully tweeted!")

            # Record that tweet was sent
            record_tweet_sent(history, repo_name, commit_hash)
            save_history(history)

            if final_image_path:
                print(f"  ✓ Image attached: {final_image_path}")
        else:
            print(f"  ✗ Failed to tweet")
            print(f"  💡 Tip: Make sure you're logged into Twitter in the browser session")

        return success

    except Exception as e:
        print(f"  ✗ Error posting to Twitter: {e}")
        print(f"\n  Troubleshooting:")
        print(f"  1. Install Playwright browsers: playwright install chromium")
        print(f"  2. Make sure you're logged into Twitter")
        print(f"  3. Check your browser automation settings")
        return False

    finally:
        # Only close browser if we created it
        if should_close_browser and browser:
            await browser.close()

        # Cleanup temp file
        if image_path and image_path.exists() and image_path != final_image_path:
            try:
                image_path.unlink()
            except:
                pass


async def main(mode: str, single_repo: str = None):
    """Main workflow: process watch list or single repository.

    Args:
        mode: Execution mode ('test', 'auto', or 'confirm')
        single_repo: Optional specific repo URL to process (bypasses watch list)
    """
    print("🚀 Git-Storyteller Social Media Automation\n")

    # Show mode banner
    mode_banners = {
        'auto': "🤖 AUTO MODE: Will tweet automatically for each repo",
        'test': "🧪 TEST MODE: Preview only - will not tweet",
        'confirm': "👤 CONFIRM MODE: Opens browser, waits for you to tweet each repo"
    }
    print(f"{mode_banners.get(mode, mode)}\n")

    # Load history
    history = load_history()

    # Process single repo if specified
    if single_repo:
        print("Processing single repository...\n")
        repo_config = {
            'name': single_repo.split('/')[-1],
            'url': single_repo,
            'enabled': True
        }
        success = await process_single_repo(repo_config, mode, history, 1, 1)
        return success

    # Process watch list (default)
    config = load_watch_list()
    watched_repos = config.get('watched_repos', [])

    # Filter enabled repos
    enabled_repos = [r for r in watched_repos if r.get('enabled', True)]

    print(f"Processing {len(enabled_repos)} repositories from watch list\n")

    results = {
        'total': len(enabled_repos),
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    # Initialize browser once for all repos (only for auto and confirm modes)
    browser = None
    if mode in ['auto', 'confirm']:
        try:
            print("🌐 Initializing browser...")
            browser = BrowserAutomation()
            await browser.initialize()
            print("  ✓ Browser ready\n")
        except Exception as e:
            print(f"  ✗ Failed to initialize browser: {e}")
            print("  ⚠️  Continuing without browser (will skip posting)\n")
            browser = None

    try:
        for i, repo_config in enumerate(enabled_repos, 1):
            success = await process_single_repo(
                repo_config,
                mode,
                history,
                i,
                len(enabled_repos),
                browser=browser
            )

        if success:
            results['success'] += 1
        else:
            results['failed'] += 1

        # Add delay between repos in auto mode to avoid rate limiting
        if i < len(enabled_repos) and mode == 'auto':
            print(f"\n⏸️  Waiting 30 seconds before next repo...")
            await asyncio.sleep(30)

    finally:
        # Close browser after all repos are processed
        if browser:
            print("\n🌐 Closing browser...")
            await browser.close()
            print("  ✓ Browser closed")

    # Print summary
    print(f"\n{'='*60}")
    print("📊 Summary")
    print(f"{'='*60}")
    print(f"  Total repos: {results['total']}")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ❌ Failed: {results['failed']}")
    print(f"  ⏭️  Skipped: {results['skipped']}")
    print(f"{'='*60}")

    return results['failed'] == 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Git-Storyteller: Analyze repositories and post to social media',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_and_tweet.py                      # Watch list mode (default)
  python analyze_and_tweet.py --test               # Test mode - preview only
  python analyze_and_tweet.py --confirm           # Confirm mode - wait for human to tweet
  python analyze_and_tweet.py --single https://github.com/user/repo
  python analyze_and_tweet.py --single https://github.com/user/repo --test
        """
    )

    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test mode: Preview only, do not post to Twitter'
    )

    parser.add_argument(
        '--confirm', '-c',
        action='store_true',
        help='Confirm mode: Open browser, wait for human to tweet each repo'
    )

    parser.add_argument(
        '--single', '-s',
        type=str,
        metavar='URL',
        help='Process a single repository (URL or path) instead of watch list'
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Determine mode
    if args.test:
        mode = 'test'
    elif args.confirm:
        mode = 'confirm'
    else:
        mode = 'auto'

    print("=" * 60)
    print("  Git-Storyteller: Social Media Automation")
    mode_labels = {
        'auto': 'Auto-Post Mode',
        'test': 'Test/Preview Mode',
        'confirm': 'Human-in-the-Loop Mode'
    }
    print(f"  MODE: {mode_labels.get(mode, mode)}")
    print("=" * 60)
    print()

    success = asyncio.run(main(mode=mode, single_repo=args.single))

    print("\n" + "=" * 60)
    if success:
        print("  ✅ Workflow completed successfully!")
    else:
        print("  ⚠️  Workflow completed with some failures")
    print("=" * 60)

    sys.exit(0 if success else 1)

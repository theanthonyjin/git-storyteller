#!/usr/bin/env python3
"""Git-Storyteller: Analyze repository and optionally post to Twitter.

Usage:
    python analyze_and_tweet.py              # Auto mode (posts without confirmation)
    python analyze_and_tweet.py --test       # Test mode (preview only, no posting)
    python analyze_and_tweet.py --confirm    # Confirmation mode (ask before posting)
    python analyze_and_tweet.py --help       # Show help
"""
import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from git_storyteller.core.git_analyzer import GitAnalyzer
from git_storyteller.core.visual_engine import VisualEngine
from git_storyteller.core.browser_automation import BrowserAutomation


def get_user_confirmation() -> bool:
    """Get user confirmation before posting to Twitter.

    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "=" * 60)
    print("  ⚠️  CONFIRMATION REQUIRED")
    print("=" * 60)
    print("\nOptions:")
    print("  [y] Yes - Post to Twitter now")
    print("  [s] Save - Save content without posting")
    print("  [n] No - Cancel and exit")
    print("\n" + "=" * 60)

    while True:
        try:
            response = input("\nPost to Twitter? (y/s/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['s', 'save']:
                print("\n💾 Content saved. Exiting without posting.")
                return False
            else:
                print("Invalid response. Please enter 'y', 's', or 'n'.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Cancelled by user")
            return False


async def main(mode: str, repo_path: str = None):
    """Run the complete autonomous storytelling workflow.

    Args:
        mode: Execution mode ('auto', 'test', or 'confirm')
        repo_path: Optional path to repository to analyze
    """
    print("🚀 Git-Storyteller Social Media Workflow\n")

    # Show mode banner
    mode_banners = {
        'auto': "🤖 AUTO MODE: Will post without confirmation",
        'test': "🧪 TEST MODE: Preview only - will not post",
        'confirm': "👤 CONFIRM MODE: Will ask before posting"
    }
    print(f"{mode_banners.get(mode, mode)}\n")

    # Step 1: Analyze repository
    print("[1/4] Analyzing repository...")
    analyzer = GitAnalyzer()

    target_path = repo_path or str(Path(__file__).parent)
    impact = analyzer.analyze(
        target=target_path,
        is_remote=False
    )

    print(f"  ✓ Repository: {impact.name}")
    print(f"  ✓ Commits analyzed: {len(impact.recent_changes)}")
    print(f"  ✓ Total commits: {impact.total_commits}")

    # Step 2: Generate visual asset
    print("\n[2/4] Generating visual asset...")
    visual_engine = VisualEngine()

    # Prepare data for bento_metrics template
    visual_data = {
        "data": {
            "repo_name": impact.name,
            "description": impact.description or "AI-native marketing agent for developers",
            "total_commits": impact.total_commits,
            "recent_count": len(impact.recent_changes),
            "marketing_hooks": impact.marketing_hooks,
            "visual_highlights": impact.visual_highlights,
        }
    }

    # Create temp file for image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        image_path = Path(f.name)

    # Render template
    try:
        screenshot = await visual_engine.render_template(
            template_name="bento_metrics",
            data=visual_data,
            commit_hash=impact.recent_changes[0].hash if impact.recent_changes else None,
            output_path=image_path,
        )
        print(f"  ✓ Visual generated: {image_path}")
        print(f"  ✓ Image size: {len(screenshot)} bytes")
    except Exception as e:
        print(f"  ✗ Failed to generate visual: {e}")
        image_path = None

    # Step 3: Generate tweet content
    print("\n[3/4] Crafting tweet content...")

    # Use the new sexy content generator
    tweet = analyzer.generate_sexy_tweet_content(impact)

    print(f"  ✓ Tweet length: {len(tweet)} characters")
    print(f"\n  Tweet preview:")
    print("  " + "─" * 50)
    for line in tweet.split("\n"):
        print(f"  {line}")
    print("  " + "─" * 50)

    # Save tweet and image to output directory
    output_dir = Path(target_path) / "output"
    output_dir.mkdir(exist_ok=True)

    # Save image to output directory
    final_image_path = None
    if image_path and image_path.exists():
        final_image_path = output_dir / "tweet_visual.png"
        import shutil
        shutil.copy(image_path, final_image_path)
        print(f"\n  💾 Image saved to: {final_image_path}")

    # Save tweet text to file
    tweet_file = output_dir / "tweet_content.txt"
    with open(tweet_file, "w") as f:
        f.write(tweet)
    print(f"  💾 Tweet text saved to: {tweet_file}")

    # Step 4: Post to Twitter (based on mode)
    if mode == 'test':
        print("\n[4/4] TEST MODE - Skipping Twitter posting")
        print("  ℹ️  To actually post, use --confirm or run without flags")
        return True

    if mode == 'confirm':
        print("\n[4/4] Ready to post to Twitter...")
        print("  ⚠️  Browser automation will open a browser window")
        print("  ⚠️  You'll need to be logged into Twitter in that browser")

        # Get user confirmation before posting
        if not get_user_confirmation():
            print("\n❌ Cancelled - Not posting to Twitter")
            print(f"   Content saved in: {output_dir}")
            return False
    else:  # auto mode
        print("\n[4/4] Posting to Twitter automatically...")
        print("  ⚠️  Browser automation will open a browser window")

    try:
        browser = BrowserAutomation()
        await browser.initialize()

        success = await browser.post_to_twitter(
            text=tweet,
            image_path=final_image_path if final_image_path else image_path,
        )

        if success:
            print("  ✓ Successfully posted to Twitter!")
            if final_image_path:
                print(f"  ✓ Image attached: {final_image_path}")
        else:
            print("  ✗ Failed to post to Twitter")
            print("  💡 Tip: Make sure you're logged into Twitter in the browser session")

        return success

    except Exception as e:
        print(f"  ✗ Error posting to Twitter: {e}")
        print("\n  Troubleshooting:")
        print("  1. Install Playwright browsers: playwright install chromium")
        print("  2. Make sure you're logged into Twitter")
        print("  3. Check your browser automation settings")
        return False

    finally:
        # Cleanup temp file
        if image_path and image_path.exists() and image_path != final_image_path:
            try:
                image_path.unlink()
            except:
                pass


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Git-Storyteller: Analyze repository and post to social media',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_and_tweet.py              # Auto mode (posts without confirmation)
  python analyze_and_tweet.py --test       # Test mode (preview only, no posting)
  python analyze_and_tweet.py --confirm    # Confirmation mode (ask before posting)
  python analyze_and_tweet.py --repo /path/to/repo --test
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
        help='Confirmation mode: Ask before posting to Twitter'
    )

    parser.add_argument(
        '--repo', '-r',
        type=str,
        default=None,
        help='Path to repository to analyze (default: current directory)'
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
        'confirm': 'Confirmation Mode'
    }
    print(f"  MODE: {mode_labels.get(mode, mode)}")
    print("=" * 60)
    print()

    success = asyncio.run(main(mode=mode, repo_path=args.repo))

    print("\n" + "=" * 60)
    if success:
        print("  ✅ Workflow completed successfully!")
    else:
        print("  ⚠️  Workflow completed")
    print("=" * 60)

    sys.exit(0 if success else 1)

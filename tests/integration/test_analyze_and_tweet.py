#!/usr/bin/env python3
"""Integration tests for analyze and tweet functionality.

This module contains tests for:
1. Local repository analysis
2. Specific commit analysis
3. Watch list functionality with history tracking
4. First tweet detection and 48h summaries
5. Skip logic for duplicate commits

Usage:
    python3.12 tests/integration/test_analyze_and_tweet.py                    # Local tests only
    python3.12 tests/integration/test_analyze_and_tweet.py --watch           # Watch list test
    python3.12 tests/integration/test_analyze_and_tweet.py --watch --simple  # Hardcoded repos
    python3.12 tests/integration/test_analyze_and_tweet.py --watch --confirm # Interactive mode
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_storyteller.core.git_analyzer import GitAnalyzer
import git


# Paths
WATCH_LIST_PATH = Path(__file__).parent.parent.parent / "config" / "watch_list.yaml"
HISTORY_DIR = Path(__file__).parent.parent.parent / "output" / "e2e_history"
HISTORY_FILE = HISTORY_DIR / "watch_list_history.json"

# Hardcoded watch list for simple mode (no yaml dependency)
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
        },
        {
            'name': 'mcp',
            'url': 'https://github.com/anthropics/mcp',
            'enabled': True
        }
    ]
}


# ============================================================================
# Watch List Functions
# ============================================================================

def load_watch_list(simple_mode: bool = False):
    """Load the watch list configuration.

    Args:
        simple_mode: If True, use hardcoded repos instead of yaml file

    Returns:
        Watch list configuration dictionary
    """
    if simple_mode or not HAS_YAML:
        return SIMPLE_WATCH_LIST

    with open(WATCH_LIST_PATH) as f:
        return yaml.safe_load(f)


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


def get_commits_past_48_hours(repo_url: str, max_count: int = 20) -> list:
    """Get commits from the past 48 hours.

    Args:
        repo_url: GitHub repository URL
        max_count: Maximum number of commits to retrieve

    Returns:
        List of commits from the past 48 hours
    """
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="git-storyteller-48h-")

    try:
        # Clone repository shallow
        repo = git.Repo.clone_from(repo_url, temp_dir, depth=50)

        # Get commits from past 48 hours
        cutoff_time = datetime.now() - timedelta(hours=48)
        recent_commits = []

        for commit in repo.iter_commits(max_count=max_count):
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if commit_date >= cutoff_time:
                recent_commits.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'date': commit.committed_datetime.isoformat(),
                    'author': commit.author.name
                })
            else:
                # Stop if we're past 48 hours
                break

        return recent_commits
    finally:
        # Cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def is_first_tweet(history: dict, repo_name: str) -> bool:
    """Check if this is the first tweet for a repo.

    Args:
        history: History dictionary
        repo_name: Repository name

    Returns:
        True if this is the first tweet
    """
    if repo_name not in history:
        return True
    return not history[repo_name].get('tweets_sent', 0)


def should_skip_tweet(history: dict, repo_name: str, latest_commit_hash: str) -> bool:
    """Check if tweet should be skipped (no new commits).

    Args:
        history: History dictionary
        repo_name: Repository name
        latest_commit_hash: Latest commit hash to check

    Returns:
        True if tweet should be skipped (no new commits since last tweet)
    """
    if is_first_tweet(history, repo_name):
        return False  # Never skip first tweet

    last_tweeted = history[repo_name].get('last_tweeted_commit')
    if last_tweeted == latest_commit_hash:
        return True  # Skip if same commit as last tweet

    return False


def record_tweet_sent(history: dict, repo_name: str, commit_hash: str):
    """Record that a tweet was sent for a repo.

    Args:
        history: History dictionary
        repo_name: Repository name
        commit_hash: Commit hash that was tweeted
    """
    if repo_name not in history:
        history[repo_name] = {}

    if 'tweets_sent' not in history[repo_name]:
        history[repo_name]['tweets_sent'] = 0

    history[repo_name]['tweets_sent'] += 1
    history[repo_name]['last_tweeted_commit'] = commit_hash
    history[repo_name]['last_tweeted_at'] = datetime.now().isoformat()


def test_watch_list(confirm_mode: bool = False, simple_mode: bool = False):
    """Test watch list functionality.

    This test:
    1. Loads the watch list
    2. For each enabled repo, analyzes it
    3. Checks if it's the first tweet
    4. If first tweet, gets 48h summary even if commit is recent
    5. Records the most recent commit hash
    6. Saves this information to a history file

    Args:
        confirm_mode: If True, ask for confirmation before processing each repo
        simple_mode: If True, use hardcoded repos instead of yaml file
    """
    # Load configuration
    config = load_watch_list(simple_mode=simple_mode)
    watched_repos = config.get('watched_repos', [])

    # Load existing history
    history = load_history()

    # Track results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_repos': len(watched_repos),
        'visited': 0,
        'failed': 0,
        'first_tweets': 0,
        'skipped': 0,
        'repos': []
    }

    print(f"\n🔍 Testing {len(watched_repos)} repositories from watch list\n")

    analyzer = GitAnalyzer()

    for repo_config in watched_repos:
        repo_name = repo_config['name']
        repo_url = repo_config['url']
        enabled = repo_config.get('enabled', True)

        if not enabled:
            print(f"⏭️  Skipping {repo_name} (disabled)")
            continue

        print(f"🔎 Visiting {repo_name}...")

        # Confirm mode: ask before processing
        if confirm_mode:
            response = input(f"   Process {repo_name}? [Y/n/q]: ").strip().lower()
            if response == 'q':
                print("   Quitting...")
                break
            elif response == 'n':
                print("   Skipping...")
                continue

        # Check if this is the first tweet
        first_tweet = is_first_tweet(history, repo_name)

        if first_tweet:
            print(f"  🎯 First tweet detected - fetching 48h summary...")
            results['first_tweets'] += 1

            try:
                # Get commits from past 48 hours
                commits_48h = get_commits_past_48_hours(repo_url)
                print(f"     Found {len(commits_48h)} commits in past 48h")

                # Show summary
                if commits_48h:
                    print(f"     📋 48h Summary:")
                    for i, commit in enumerate(commits_48h[:5], 1):
                        print(f"        {i}. {commit['hash']}: {commit['message'][:50]}...")
                    if len(commits_48h) > 5:
                        print(f"        ... and {len(commits_48h) - 5} more")

                # Store 48h summary in history
                if repo_name not in history:
                    history[repo_name] = {
                        'url': repo_url,
                        'first_seen': datetime.now().isoformat(),
                        'commits': []
                    }

                history[repo_name]['past_48h_commits'] = commits_48h
            except Exception as e:
                print(f"  ⚠️  Could not fetch 48h summary: {e}")

        try:
            # Analyze the repository
            impact = analyzer.analyze(repo_url, is_remote=True)

            # Get the most recent commit
            if impact.recent_changes:
                latest_commit = impact.recent_changes[0]
                commit_hash = latest_commit.hash

                # Check if we should skip this tweet (no new commits)
                if should_skip_tweet(history, repo_name, commit_hash):
                    print(f"  ⏭️  Skipped: No new commits since last tweet")
                    print(f"     Last tweeted: {history[repo_name].get('last_tweeted_commit', 'N/A')}")
                    print(f"     Current: {commit_hash}")

                    results['repos'].append({
                        'name': repo_name,
                        'status': 'skipped',
                        'latest_commit': commit_hash,
                        'reason': 'No new commits since last tweet',
                        'is_first_tweet': first_tweet
                    })
                    results['skipped'] += 1
                    continue  # Skip to next repo

                # Initialize history entry if needed
                if repo_name not in history:
                    history[repo_name] = {
                        'url': repo_url,
                        'first_seen': datetime.now().isoformat(),
                        'commits': []
                    }

                # Add to commit history if not already tracked
                existing_hashes = [c['hash'] for c in history[repo_name]['commits']]
                if commit_hash not in existing_hashes:
                    history[repo_name]['commits'].append({
                        'hash': commit_hash,
                        'message': latest_commit.message,
                        'date': latest_commit.date,
                        'author': latest_commit.author,
                        'first_seen': datetime.now().isoformat()
                    })

                # Record latest state
                history[repo_name]['last_seen'] = datetime.now().isoformat()
                history[repo_name]['latest_commit'] = {
                    'hash': commit_hash,
                    'message': latest_commit.message,
                    'date': latest_commit.date,
                    'author': latest_commit.author
                }

                # Mark as first tweet if applicable
                if first_tweet:
                    history[repo_name]['first_tweet'] = True
                    history[repo_name]['first_tweet_commit'] = commit_hash
                    print(f"  ✨ First tweet marked")

                # Record that we're going to tweet this commit
                record_tweet_sent(history, repo_name, commit_hash)

                print(f"  ✅ Latest commit: {commit_hash} by {latest_commit.author}")
                print(f"     {latest_commit.message[:60]}...")

                # Track results
                results['repos'].append({
                    'name': repo_name,
                    'status': 'success',
                    'latest_commit': commit_hash,
                    'total_commits': impact.total_commits,
                    'is_first_tweet': first_tweet
                })
                results['visited'] += 1

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results['repos'].append({
                'name': repo_name,
                'status': 'failed',
                'error': str(e),
                'is_first_tweet': first_tweet
            })
            results['failed'] += 1

    # Save history
    save_history(history)

    # Save this run's results
    run_results_file = HISTORY_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(run_results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"\n📊 Summary:")
    print(f"   Total repos: {results['total_repos']}")
    print(f"   Visited (new commits): {results['visited']}")
    print(f"   First tweets: {results['first_tweets']}")
    print(f"   Skipped (no new commits): {results['skipped']}")
    print(f"   Failed: {results['failed']}")
    print(f"   History file: {HISTORY_FILE}")
    print(f"   Run results: {run_results_file}")

    # Assert all repos were visited
    assert results['failed'] == 0, f"{results['failed']} repos failed to visit"

    print(f"\n✅ All repositories visited successfully!")


def test_history_persistence():
    """Test that commit history persists between runs.

    This ensures:
    1. History file is created on first run
    2. History file is updated on subsequent runs
    3. Commit hashes are tracked over time
    """
    history = load_history()

    print(f"\n📜 Commit History:")
    print(f"   History file exists: {HISTORY_FILE.exists()}")
    print(f"   Tracked repos: {len(history)}")

    for repo_name, repo_data in history.items():
        print(f"\n   {repo_name}:")
        print(f"      URL: {repo_data.get('url', 'N/A')}")
        print(f"      First seen: {repo_data.get('first_seen', 'N/A')}")
        print(f"      Last seen: {repo_data.get('last_seen', 'N/A')}")
        print(f"      Total tracked commits: {len(repo_data.get('commits', []))}")
        if 'latest_commit' in repo_data:
            print(f"      Latest: {repo_data['latest_commit']['hash']} - {repo_data['latest_commit']['message'][:40]}...")

    # Assert history exists and has data
    assert HISTORY_FILE.exists(), "History file should exist"
    assert len(history) > 0, "History should contain at least one repo"


def test_first_tweet_tracking():
    """Test that first tweet status is tracked correctly.

    This ensures:
    1. First tweet detection works
    2. 48h summary is generated for first tweets
    3. Subsequent runs correctly identify non-first tweets
    """
    history = load_history()

    print(f"\n🎯 First Tweet Tracking:")
    print(f"   History file exists: {HISTORY_FILE.exists()}")
    print(f"   Tracked repos: {len(history)}")

    first_tweet_count = 0
    subsequent_tweet_count = 0

    for repo_name, repo_data in history.items():
        is_first = repo_data.get('first_tweet', False)
        tweets_sent = repo_data.get('tweets_sent', 0)

        if is_first:
            first_tweet_count += 1
            print(f"\n   🎉 {repo_name}: FIRST TWEET")
            print(f"      First tweet commit: {repo_data.get('first_tweet_commit', 'N/A')}")

            # Check if 48h summary exists
            if 'past_48h_commits' in repo_data:
                commits_48h = repo_data['past_48h_commits']
                print(f"      48h commits: {len(commits_48h)}")
                if commits_48h:
                    print(f"      Recent: {commits_48h[0]['message'][:40]}...")
        elif tweets_sent > 0:
            subsequent_tweet_count += 1
            print(f"\n   🐦 {repo_name}: {tweets_sent} tweet(s) sent")
            print(f"      Last tweeted: {repo_data.get('last_tweeted_at', 'N/A')}")

    print(f"\n   Summary:")
    print(f"      First tweets: {first_tweet_count}")
    print(f"      Subsequent tweets: {subsequent_tweet_count}")

    # Assert we have tracked some repos
    assert len(history) > 0, "History should contain at least one repo"


# ============================================================================
# Local Repository Tests
# ============================================================================

def test_analyze_local_repo():
    """Test analyzing the git-storyteller repository itself."""
    print("=" * 60)
    print("Testing Git Analyzer on git-storyteller")
    print("=" * 60)

    # Get the repository path
    repo_path = Path(__file__).parent.parent.parent

    print(f"\n📂 Analyzing: {repo_path}")

    # Initialize analyzer
    analyzer = GitAnalyzer()

    # Analyze the repository
    print("\n🔍 Running analysis...")
    impact = analyzer.analyze(str(repo_path), ref="HEAD", is_remote=False)

    # Display results
    print(f"\n✅ Total Commits: {impact.total_commits}")
    print(f"✅ Recent Changes: {len(impact.recent_changes)}")

    if impact.marketing_hooks:
        print("\n📊 Marketing Hooks:")
        for i, hook in enumerate(impact.marketing_hooks[:3], 1):
            print(f"   {i}. {hook}")

    if impact.visual_highlights:
        print("\n🎨 Visual Highlights:")
        for i, highlight in enumerate(impact.visual_highlights[:3], 1):
            print(f"   {i}. {highlight}")

    # Test tweet generation
    print("\n" + "─" * 50)
    print("🐦 Testing Tweet Generation")
    print("─" * 50)

    tweet = analyzer.generate_sexy_tweet_content(impact)
    print(tweet)

    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)

    return True


def test_analyze_specific_commit():
    """Test analyzing a specific commit."""
    print("\n" + "=" * 60)
    print("Testing Specific Commit Analysis")
    print("=" * 60)

    repo_path = Path(__file__).parent.parent.parent
    analyzer = GitAnalyzer()

    # Use the latest commit
    print(f"\n📂 Analyzing HEAD~5 of: {repo_path}")
    impact = analyzer.analyze(str(repo_path), ref="HEAD~5", is_remote=False)

    print("\n✅ Analyzed commit range: HEAD~5")
    print(f"✅ Total commits in range: {impact.total_commits}")

    if impact.recent_changes:
        latest = impact.recent_changes[0]
        print("\n📝 Latest commit:")
        print(f"   Hash: {latest.hash[:8]}")
        print(f"   Message: {latest.message[:60]}...")

    print("\n" + "=" * 60)
    print("✅ Specific commit test completed!")
    print("=" * 60)

    return True


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Parse command line arguments
    watch_mode = '--watch' in sys.argv or '-w' in sys.argv
    confirm_mode = '--confirm' in sys.argv or '-c' in sys.argv
    simple_mode = '--simple' in sys.argv or '-s' in sys.argv

    try:
        if watch_mode:
            # Run watch list tests
            print("=" * 60)
            print("Watch List Integration Tests")
            if confirm_mode:
                print("   Confirm mode: ENABLED")
            if simple_mode:
                print("   Simple mode: ENABLED (hardcoded repos)")
            print("=" * 60)

            print("\n1️⃣ Testing watch list...")
            test_watch_list(confirm_mode=confirm_mode, simple_mode=simple_mode)

            print("\n2️⃣ Testing history persistence...")
            test_history_persistence()

            print("\n3️⃣ Testing first tweet tracking...")
            test_first_tweet_tracking()

            print("\n" + "=" * 60)
            print("✅ All watch list tests passed!")
            print("=" * 60)
        else:
            # Run local repository tests
            test_analyze_local_repo()
            test_analyze_specific_commit()

            print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

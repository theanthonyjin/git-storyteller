"""E2E test for watch list functionality.

This test:
1. Visits each repo in the watch list one by one
2. Records the most recent commit for each repo
3. Maintains a history of commits for tracking
4. Tracks first tweet status and generates 48h summary for new repos

Usage:
    python3.12 tests/integration/test_watch_list_e2e.py --confirm  # Full watch list
    python3.12 tests/integration/test_watch_list_e2e.py --simple   # Hardcoded repos
    python3.12 tests/integration/test_watch_list_e2e.py --simple --confirm  # Both
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

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


def test_visit_each_repo_in_watch_list(confirm_mode: bool = False, simple_mode: bool = False):
    """Test visiting each repository in the watch list.

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


def test_tweet_generation_for_each_repo():
    """Test tweet generation for each watched repository.

    This ensures:
    1. Each repo can generate tweet content
    2. Tweet content includes proper formatting
    3. GitHub references are included
    """
    config = load_watch_list()
    watched_repos = config.get('watched_repos', [])

    analyzer = GitAnalyzer()

    print(f"\n🐦 Testing tweet generation for {len(watched_repos)} repos\n")

    for repo_config in watched_repos:
        repo_name = repo_config['name']
        repo_url = repo_config['url']
        enabled = repo_config.get('enabled', True)

        if not enabled:
            continue

        print(f"📝 Generating tweet for {repo_name}...")

        try:
            # Analyze repository
            impact = analyzer.analyze(repo_url, is_remote=True)

            # Generate tweet
            tweet = analyzer.generate_sexy_tweet_content(impact, repo_url=repo_url)

            print(f"  ✅ Tweet generated ({len(tweet)} chars)")
            print(f"     Preview: {tweet[:100]}...")

            # Assert tweet has content
            assert len(tweet) > 0, f"Tweet should not be empty for {repo_name}"
            assert repo_name in tweet or repo_url.split('/')[-1] in tweet, "Tweet should reference repo"

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            raise

    print(f"\n✅ Tweet generation successful for all repos!")


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


if __name__ == "__main__":
    import sys

    # Check for flags
    confirm_mode = '--confirm' in sys.argv or '-c' in sys.argv
    simple_mode = '--simple' in sys.argv or '-s' in sys.argv

    print("=" * 60)
    print("E2E Test: Watch List Functionality")
    if confirm_mode:
        print("   Confirm mode: ENABLED")
    if simple_mode:
        print("   Simple mode: ENABLED (hardcoded repos)")
    print("=" * 60)

    # Run tests
    print("\n1️⃣ Testing visit each repo in watch list...")
    test_visit_each_repo_in_watch_list(confirm_mode=confirm_mode, simple_mode=simple_mode)

    print("\n2️⃣ Testing history persistence...")
    test_history_persistence()

    print("\n3️⃣ Testing first tweet tracking...")
    test_first_tweet_tracking()

    print("\n" + "=" * 60)
    print("✅ All E2E tests passed!")
    print("=" * 60)

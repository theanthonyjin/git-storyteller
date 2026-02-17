"""E2E test for watch list functionality.

This test:
1. Visits each repo in the watch list one by one
2. Records the most recent commit for each repo
3. Maintains a history of commits for tracking
"""
import json
from pathlib import Path
from datetime import datetime

import yaml
from git_storyteller.core.git_analyzer import GitAnalyzer


# Paths
WATCH_LIST_PATH = Path(__file__).parent.parent.parent / "config" / "watch_list.yaml"
HISTORY_DIR = Path(__file__).parent.parent.parent / "output" / "e2e_history"
HISTORY_FILE = HISTORY_DIR / "watch_list_history.json"


def load_watch_list():
    """Load the watch list configuration."""
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


def test_visit_each_repo_in_watch_list():
    """Test visiting each repository in the watch list.

    This test:
    1. Loads the watch list
    2. For each enabled repo, analyzes it
    3. Records the most recent commit hash
    4. Saves this information to a history file
    """
    # Load configuration
    config = load_watch_list()
    watched_repos = config.get('watched_repos', [])

    # Load existing history
    history = load_history()

    # Track results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_repos': len(watched_repos),
        'visited': 0,
        'failed': 0,
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

        try:
            # Analyze the repository
            impact = analyzer.analyze(repo_url, is_remote=True)

            # Get the most recent commit
            if impact.recent_changes:
                latest_commit = impact.recent_changes[0]
                commit_hash = latest_commit.hash

                # Record in history
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

                print(f"  ✅ Latest commit: {commit_hash} by {latest_commit.author}")
                print(f"     {latest_commit.message[:60]}...")

                # Track results
                results['repos'].append({
                    'name': repo_name,
                    'status': 'success',
                    'latest_commit': commit_hash,
                    'total_commits': impact.total_commits
                })
                results['visited'] += 1

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results['repos'].append({
                'name': repo_name,
                'status': 'failed',
                'error': str(e)
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
    print(f"   Visited successfully: {results['visited']}")
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


if __name__ == "__main__":
    print("=" * 60)
    print("E2E Test: Watch List Functionality")
    print("=" * 60)

    # Run tests
    print("\n1️⃣ Testing visit each repo in watch list...")
    test_visit_each_repo_in_watch_list()

    print("\n2️⃣ Testing history persistence...")
    test_history_persistence()

    print("\n3️⃣ Testing tweet generation...")
    test_tweet_generation_for_each_repo()

    print("\n" + "=" * 60)
    print("✅ All E2E tests passed!")
    print("=" * 60)

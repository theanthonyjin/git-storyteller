#!/usr/bin/env python3
"""Simplified test script for watch list with confirm mode (no yaml dependency)."""
import json
from pathlib import Path
from datetime import datetime
from git_storyteller.core.git_analyzer import GitAnalyzer

# Hardcoded watch list for testing (subset of repos)
WATCHED_REPOS = [
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

HISTORY_DIR = Path(__file__).parent.parent / "output" / "e2e_history"
HISTORY_FILE = HISTORY_DIR / "watch_list_history.json"


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


def main(confirm_mode: bool = True):
    """Run the watch list test."""
    print("=" * 60)
    print("Watch List Test (Simplified)")
    if confirm_mode:
        print("   Confirm mode: ENABLED")
    print("=" * 60)

    history = load_history()
    analyzer = GitAnalyzer()

    for repo_config in WATCHED_REPOS:
        repo_name = repo_config['name']
        repo_url = repo_config['url']

        if not repo_config.get('enabled', True):
            print(f"⏭️  Skipping {repo_name} (disabled)")
            continue

        print(f"\n🔎 {repo_name}")
        print(f"   URL: {repo_url}")

        # Confirm mode
        if confirm_mode:
            response = input(f"   Process {repo_name}? [Y/n/q]: ").strip().lower()
            if response == 'q':
                print("   Quitting...")
                break
            elif response == 'n':
                print("   Skipping...")
                continue

        try:
            # Analyze repository
            print(f"   Analyzing...")
            impact = analyzer.analyze(repo_url, is_remote=True)

            if impact.recent_changes:
                latest_commit = impact.recent_changes[0]
                commit_hash = latest_commit.hash

                # Check if first tweet
                first_tweet = is_first_tweet(history, repo_name)
                if first_tweet:
                    print(f"   🎯 First tweet detected!")

                # Check if should skip
                if should_skip_tweet(history, repo_name, commit_hash):
                    print(f"   ⏭️  Skipped: No new commits")
                    print(f"      Last tweeted: {history[repo_name].get('last_tweeted_commit')}")
                    print(f"      Current: {commit_hash}")
                    continue

                # Show commit info
                print(f"   ✅ Latest commit: {commit_hash}")
                print(f"      Author: {latest_commit.author}")
                print(f"      Message: {latest_commit.message[:80]}...")

                # Initialize history if needed
                if repo_name not in history:
                    history[repo_name] = {
                        'url': repo_url,
                        'first_seen': datetime.now().isoformat(),
                        'commits': []
                    }

                # Record tweet
                record_tweet_sent(history, repo_name, commit_hash)

                if first_tweet:
                    history[repo_name]['first_tweet'] = True
                    history[repo_name]['first_tweet_commit'] = commit_hash

                # Save history after each repo
                save_history(history)
                print(f"   💾 Saved to history")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print(f"History saved to: {HISTORY_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    confirm_mode = '--no-confirm' not in sys.argv
    main(confirm_mode=confirm_mode)

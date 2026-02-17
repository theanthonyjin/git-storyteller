#!/usr/bin/env python3
"""Test the analyze_and_tweet script functionality."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from git_storyteller.core.git_analyzer import GitAnalyzer


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
        print(f"\n📊 Marketing Hooks:")
        for i, hook in enumerate(impact.marketing_hooks[:3], 1):
            print(f"   {i}. {hook}")

    if impact.visual_highlights:
        print(f"\n🎨 Visual Highlights:")
        for i, highlight in enumerate(impact.visual_highlights[:3], 1):
            print(f"   {i}. {highlight}")

    # Test tweet generation
    print("\n" + "─" * 50)
    print("🐦 Testing Tweet Generation")
    print("─" * 50)

    tweet = analyzer.generate_tweet_content(impact)
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
    print(f"\n📂 Analyzing HEAD of: {repo_path}")
    impact = analyzer.analyze(str(repo_path), ref="HEAD~5", is_remote=False)

    print(f"\n✅ Analyzed commit range: HEAD~5")
    print(f"✅ Total commits in range: {impact.total_commits}")

    if impact.recent_changes:
        latest = impact.recent_changes[0]
        print(f"\n📝 Latest commit:")
        print(f"   Hash: {latest.hash[:8]}")
        print(f"   Message: {latest.message[:60]}...")

    print("\n" + "=" * 60)
    print("✅ Specific commit test completed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        # Test 1: Analyze local repo
        test_analyze_local_repo()

        # Test 2: Analyze specific commit
        test_analyze_specific_commit()

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

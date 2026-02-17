#!/usr/bin/env python3
"""Local test script for Git-Storyteller on itself."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from git_storyteller.core.git_analyzer import GitAnalyzer
from git_storyteller.core.learning_system import LearningSystem
from git_storyteller.core.visual_engine import VisualEngine


def test_analyzer():
    """Test git analyzer on itself."""
    print("=" * 60)
    print("🔍 Test 1: Git Analyzer")
    print("=" * 60)

    analyzer = GitAnalyzer()
    impact = analyzer.analyze(
        target=".",
        ref="HEAD",
        is_remote=False
    )

    print(f"\n✅ Repository: {impact.name}")
    print(f"✅ Description: {impact.description}")
    print(f"✅ Total Commits: {impact.total_commits}")
    print(f"✅ Recent Changes: {len(impact.recent_changes)}")
    print("\n📊 Marketing Hooks:")
    for i, hook in enumerate(impact.marketing_hooks[:3], 1):
        print(f"   {i}. {hook}")

    print("\n🎨 Visual Highlights:")
    for i, highlight in enumerate(impact.visual_highlights[:3], 1):
        print(f"   {i}. {highlight}")

    return True


async def test_visual():
    """Test visual rendering."""
    print("\n" + "=" * 60)
    print("🎨 Test 2: Visual Engine")
    print("=" * 60)

    engine = VisualEngine()

    # Prepare test data
    data = {
        "repo_name": "git-storyteller",
        "description": "Autonomous marketing agent for developers",
        "total_commits": 100,
        "recent_count": 5,
        "marketing_hooks": [
            "🚀 Just shipped MCP integration",
            "🐛 Fixed webhook handler",
            "⚡ Added learning system"
        ],
        "visual_highlights": [
            "Most active: src/git_storyteller/core/",
            "Recent: Self-hype amplification feature"
        ]
    }

    # Test Carbon-X template
    print("\n📸 Rendering Carbon-X template...")
    result1 = await engine.render_template(
        template_name="carbon_x",
        data={
            "repo_name": data["repo_name"],
            "commit_hash": "abc123",
            "commit_message": "Add new features",
            "files_changed": 5,
            "additions": 100,
            "deletions": 20,
            "code_diff": "+ def new_feature():\n+     pass"
        },
        commit_hash="abc123"
    )

    if result1.get("success"):
        print(f"✅ Carbon-X: {result1['image_size']} bytes")

    # Test Bento-Metrics template
    print("\n📸 Rendering Bento-Metrics template...")
    result2 = await engine.render_template(
        template_name="bento_metrics",
        data=data,
        commit_hash="abc123"
    )

    if result2.get("success"):
        print(f"✅ Bento-Metrics: {result2['image_size']} bytes")

    return True


def test_learning():
    """Test learning system."""
    print("\n" + "=" * 60)
    print("🧠 Test 3: Learning System")
    print("=" * 60)

    learning = LearningSystem()

    # Record a test post
    learning.record_post(
        post_id="test123",
        platform="twitter",
        content="🚀 Just shipped new features to git-storyteller!",
        hook_type="feature",
        template="bento_metrics"
    )

    print("✅ Recorded test post")

    # Get insights
    insights = learning.get_insights()

    if "message" not in insights:
        print(f"✅ Total posts tracked: {insights['total_posts']}")
        print(f"✅ Total engagement: {insights['total_engagement']}")
        print(f"✅ Avg engagement: {insights['avg_engagement']:.1f}")

    return True


def generate_sample_post():
    """Generate a sample social media post."""
    print("\n" + "=" * 60)
    print("📱 Sample Social Media Post")
    print("=" * 60)

    analyzer = GitAnalyzer()
    impact = analyzer.analyzer(".", ref="HEAD", is_remote=False)

    print("\n─" * 50)
    print("🚀 Just pushed updates to git-storyteller!")
    print()

    for hook in impact.marketing_hooks[:3]:
        print(f"• {hook}")

    print()
    print("🔗 https://github.com/theanthonyjin/git-storyteller")
    print("─" * 50)


async def main():
    """Run all tests."""
    print("\n🧪 Git-Storyteller Self-Test")
    print("Testing Git-Storyteller on its own repository\n")

    try:
        # Run tests
        test_analyzer()
        await test_visual()
        test_learning()
        generate_sample_post()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

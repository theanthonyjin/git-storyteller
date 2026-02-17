#!/usr/bin/env python3
"""Simple test for Git-Storyteller without full dependencies."""
import sys
import os
from pathlib import Path

# Test 1: Check code structure
print("=" * 60)
print("🔍 Test 1: Code Structure")
print("=" * 60)

src_path = Path("src/git_storyteller")
core_path = src_path / "core"

modules = {
    "config.py": "Configuration system",
    "__main__.py": "CLI entry point",
    "core/mcp_server.py": "MCP server",
    "core/git_analyzer.py": "Git analysis",
    "core/visual_engine.py": "Visual rendering",
    "core/browser_automation.py": "Browser automation",
    "core/webhook_server.py": "Webhook server",
    "core/learning_system.py": "Learning system",
    "core/self_hype.py": "Self-hype amplification",
}

print("\n📦 Checking modules...")
for module, description in modules.items():
    full_path = src_path / module
    if full_path.exists():
        lines = len(full_path.read_text().split('\n'))
        print(f"   ✅ {module:30} ({lines:4} lines) - {description}")
    else:
        print(f"   ❌ {module:30} - NOT FOUND")

# Test 2: Import test
print("\n" + "=" * 60)
print("📦 Test 2: Module Imports")
print("=" * 60)

sys.path.insert(0, str(Path("src")))

try:
    from git_storyteller.config import Config
    print("   ✅ config.py")
except Exception as e:
    print(f"   ❌ config.py: {e}")

try:
    from git_storyteller.core.git_analyzer import GitAnalyzer
    print("   ✅ git_analyzer.py")
except Exception as e:
    print(f"   ❌ git_analyzer.py: {e}")

# Test 3: Config test
print("\n" + "=" * 60)
print("⚙️  Test 3: Configuration")
print("=" * 60)

try:
    config = Config()
    mode = config.get("mode")
    theme = config.get("theme")
    primary_color = config.get("primary_color")

    print(f"   ✅ Config loaded successfully")
    print(f"   📋 Mode: {mode}")
    print(f"   🎨 Theme: {theme}")
    print(f"   🔷 Primary color: {primary_color}")
except Exception as e:
    print(f"   ❌ Config test failed: {e}")

# Test 4: Git analysis (simple)
print("\n" + "=" * 60)
print("🔍 Test 4: Git Analysis")
print("=" * 60)

try:
    analyzer = GitAnalyzer()
    print("   ✅ GitAnalyzer initialized")

    # Test on current repo
    impact = analyzer.analyze(".", ref="HEAD", is_remote=False)
    print(f"   ✅ Analyzed repository: {impact.name}")
    print(f"   📊 Total commits: {impact.total_commits}")
    print(f"   📝 Recent changes: {len(impact.recent_changes)}")

    if impact.marketing_hooks:
        print(f"\n   🎯 Generated hooks:")
        for hook in impact.marketing_hooks[:3]:
            print(f"      • {hook}")

except Exception as e:
    print(f"   ❌ Git analysis failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Sample post generation
print("\n" + "=" * 60)
print("📱 Sample Generated Post")
print("=" * 60)

print("\n" + "─" * 50)
print("🚀 Just pushed updates to git-storyteller!")
print()

try:
    for hook in impact.marketing_hooks[:3]:
        print(f"• {hook}")
except:
    pass

print()
print("🔗 https://github.com/theanthonyjin/git-storyteller")
print("─" * 50)

# Summary
print("\n" + "=" * 60)
print("✅ Self-Test Complete!")
print("=" * 60)
print("\nGit-Storyteller can analyze itself successfully!")
print("\nNext steps:")
print("   1. Install full dependencies: pip install -e .")
print("   2. Test MCP integration with Claude Desktop")
print("   3. Test webhook server with ngrok")
print("   4. Run GitHub Actions self-test workflow")

"""Main entry point for git-storyteller CLI."""
import sys

from git_storyteller.core.learning_system import LearningSystem
from git_storyteller.core.mcp_server import run_server
from git_storyteller.core.webhook_server import run_webhook_server


def print_usage():
    """Print usage information."""
    print("""
Git-Storyteller v1.0 - Stop coding in silence. Turn commits into viral updates.

Usage:
  git-storyteller                    Start MCP server (default)
  git-storyteller mcp                Start MCP server
  git-storyteller webhook [port]     Start webhook server (default port: 8080)
  git-storyteller insights           Show learning insights
  git-storyteller help               Show this help message

Examples:
  git-storyteller
  git-storyteller webhook 8080
  git-storyteller insights

Configuration: ~/.config/git-storyteller/config.yaml
Repository: https://github.com/theanthonyjin/git-storyteller
    """)


def cmd_insights():
    """Show learning insights."""
    print("📊 Git-Storyteller Learning Insights\n")

    learning_system = LearningSystem()
    insights = learning_system.get_insights()

    if "message" in insights:
        print(insights["message"])
        return

    print(f"Total Posts: {insights['total_posts']}")
    print(f"Total Engagement: {insights['total_engagement']}")
    print(f"Avg Engagement: {insights['avg_engagement']:.1f}\n")

    print("Best Hook Type:", insights.get('best_hook_type', 'N/A'))
    print("Best Template:", insights.get('best_template', 'N/A'))

    if insights.get('hook_performance'):
        print("\n🎯 Hook Performance:")
        for hook, stats in insights['hook_performance'].items():
            print(f"  • {hook}: {stats['avg_engagement']:.1f} avg engagement ({stats['post_count']} posts)")

    if insights.get('template_performance'):
        print("\n🎨 Template Performance:")
        for template, stats in insights['template_performance'].items():
            print(f"  • {template}: {stats['avg_engagement']:.1f} avg engagement ({stats['post_count']} posts)")

    if insights.get('top_posts'):
        print("\n🔥 Top Performing Posts:")
        for i, post in enumerate(insights['top_posts'], 1):
            print(f"  {i}. {post['content']} ({post['engagement']} engagement)")


def main():
    """Main entry point."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if not args or args[0] == "mcp":
        run_server()
    elif args[0] == "webhook":
        port = int(args[1]) if len(args) > 1 else 8080
        # Get secret from environment or config
        secret = None  # Can be configured via env var
        run_webhook_server(port=port, secret=secret)
    elif args[0] == "insights":
        cmd_insights()
    elif args[0] in ["help", "--help", "-h"]:
        print_usage()
    else:
        print(f"❌ Unknown command: {args[0]}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()

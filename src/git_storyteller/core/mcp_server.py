"""MCP server implementation for git-storyteller."""
import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from ..config import get_config
from .browser_automation import BrowserAutomation
from .git_analyzer import GitAnalyzer
from .visual_engine import VisualEngine

# Create MCP server
mcp = FastMCP(name="git-storyteller")

# Initialize components
git_analyzer = GitAnalyzer()
visual_engine = VisualEngine()
browser_automation: Optional[BrowserAutomation] = None


def get_browser() -> BrowserAutomation:
    """Get or initialize browser automation instance.

    Returns:
        BrowserAutomation instance
    """
    global browser_automation
    if browser_automation is None:
        browser_automation = BrowserAutomation()
    return browser_automation


@mcp.tool()
async def analyze_repository_impact(
    target: str,
    ref: Optional[str] = None,
) -> dict:
    """Analyze local or remote repository for marketing value.

    Args:
        target: Local repository path or GitHub URL
        ref: Optional commit hash, branch, or PR reference

    Returns:
        Dictionary with repository analysis including:
        - name: Repository name
        - description: Repository description
        - recent_changes: List of recent commits
        - total_commits: Total commit count
        - marketing_hooks: List of marketing hook strings
        - visual_highlights: List of visual highlight strings
    """
    # Determine if target is a remote URL
    is_remote = target.startswith(("http://", "https://", "git@github.com:"))

    try:
        # Analyze repository
        impact = git_analyzer.analyze(target, ref=ref, is_remote=is_remote)

        return {
            "name": impact.name,
            "description": impact.description,
            "recent_changes": [
                {
                    "hash": c.hash,
                    "author": c.author,
                    "message": c.message,
                    "date": c.date,
                    "files_changed": c.files_changed,
                    "semantic_impact": c.semantic_impact,
                }
                for c in impact.recent_changes
            ],
            "total_commits": impact.total_commits,
            "marketing_hooks": impact.marketing_hooks,
            "visual_highlights": impact.visual_highlights,
        }

    except Exception as e:
        return {
            "error": f"Failed to analyze repository: {str(e)}",
            "target": target,
        }


@mcp.tool()
async def summarize_milestone_impact(
    target: str,
    hours: Optional[int] = 24,
) -> dict:
    """Summarize cumulative impact over a time period.

    This is perfect for creating "What I built today" posts that aggregate
    multiple small commits into a compelling story.

    Args:
        target: Local repository path or GitHub URL
        hours: Number of hours to look back (default: 24)

    Returns:
        Dictionary with milestone summary including:
        - commit_count: Number of commits in the period
        - impact_summary: Overall impact description
        - top_changes: Most significant changes
        - marketing_hooks: Marketing-friendly hooks
        - suggested_caption: Pre-written social media caption
    """
    try:
        # Analyze repository
        is_remote = target.startswith(("http://", "https://", "git@github.com:"))
        impact = git_analyzer.analyze(target, ref=None, is_remote=is_remote)

        # Calculate milestone metrics
        commit_count = len(impact.recent_changes)
        impact_types = [c.semantic_impact for c in impact.recent_changes]

        # Generate impact summary
        feat_count = sum(1 for t in impact_types if "feature" in t.lower())
        fix_count = sum(1 for t in impact_types if "bug fix" in t.lower())

        impact_summary = f"Made {commit_count} commits"
        if feat_count > 0:
            impact_summary += f", shipped {feat_count} new feature{'s' if feat_count > 1 else ''}"
        if fix_count > 0:
            impact_summary += f", fixed {fix_count} bug{'s' if fix_count > 1 else ''}"

        # Get top changes
        top_changes = impact.recent_changes[:3]

        # Generate suggested caption
        caption = f"🚀 Just pushed {commit_count} commits to {impact.name}!\n\n"
        caption += f"{impact_summary}\n\n"
        caption += "Highlights:\n"
        for hook in impact.marketing_hooks[:3]:
            caption += f"• {hook}\n"
        caption += "\n#coding #devlife"

        return {
            "commit_count": commit_count,
            "impact_summary": impact_summary,
            "top_changes": [
                {
                    "message": c.message,
                    "hash": c.hash,
                    "semantic_impact": c.semantic_impact,
                }
                for c in top_changes
            ],
            "marketing_hooks": impact.marketing_hooks,
            "suggested_caption": caption,
            "repo_name": impact.name,
        }

    except Exception as e:
        return {
            "error": f"Failed to summarize milestone: {str(e)}",
            "target": target,
        }


@mcp.tool()
async def dynamic_template_render(
    template_name: str,
    data: dict,
    commit_hash: Optional[str] = None,
    output_path: Optional[str] = None,
) -> dict:
    """Render a visual template with data-driven styling.

    Uses entropy seeding based on commit hash to create unique but
    deterministic visual variations.

    Args:
        template_name: Template name ("carbon_x" or "bento_metrics")
        data: Data to populate template with
        commit_hash: Optional commit hash for entropy seeding
        output_path: Optional path to save rendered image

    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - image_path: Path to saved image (if output_path provided)
        - image_size: Size of image in bytes
        - template_used: Name of template used
    """
    try:
        # Render template
        screenshot = await visual_engine.render_template(
            template_name=template_name,
            data=data,
            commit_hash=commit_hash,
            output_path=Path(output_path) if output_path else None,
        )

        result = {
            "success": True,
            "template_used": template_name,
            "image_size": len(screenshot),
        }

        if output_path:
            result["image_path"] = str(output_path)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to render template: {str(e)}",
            "template_used": template_name,
        }


@mcp.tool()
async def stealth_browser_dispatcher(
    platform: str,
    text: str,
    image_path: Optional[str] = None,
    scheduled_at: Optional[str] = None,
) -> dict:
    """Dispatch a social media post with stealth automation.

    Reuses your browser session for authentication and simulates human
    behavior patterns to avoid detection.

    Args:
        platform: Platform to post to ("twitter" or "linkedin")
        text: Post content/text
        image_path: Optional path to image to attach
        scheduled_at: Optional schedule time in HH:MM format (e.g., "09:00")

    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - platform: Platform posted to
        - scheduled: Boolean indicating if post was scheduled
        - post_url: URL of posted content (if available)
    """
    try:
        # Initialize browser if needed
        browser = get_browser()
        await browser.initialize()

        # Wait for scheduled time if specified
        if scheduled_at:
            await browser.wait_for_scheduled_time(scheduled_at)

        # Post to appropriate platform
        if platform == "twitter":
            success = await browser.post_to_twitter(
                text=text,
                image_path=Path(image_path) if image_path else None,
                scheduled_at=scheduled_at,
            )
        elif platform == "linkedin":
            success = await browser.post_to_linkedin(
                text=text,
                image_path=Path(image_path) if image_path else None,
            )
        else:
            return {
                "success": False,
                "error": f"Unsupported platform: {platform}",
            }

        return {
            "success": success,
            "platform": platform,
            "scheduled": scheduled_at is not None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to dispatch post: {str(e)}",
            "platform": platform,
        }


@mcp.tool()
async def fetch_engagement_feedback(platform: str, limit: int = 5) -> dict:
    """Fetch engagement metrics from recent posts.

    This data is stored locally and used to optimize future content
    generation through a feedback loop.

    Args:
        platform: Platform to fetch from ("twitter" or "linkedin")
        limit: Number of recent posts to analyze (default: 5)

    Returns:
        Dictionary with:
        - platform: Platform name
        - posts: List of post metrics
        - total_engagement: Combined engagement score
        - learnings: Insights for future optimization
    """
    config = get_config()

    try:
        # Initialize browser if needed
        browser = get_browser()
        await browser.initialize()

        # Fetch metrics
        metrics = await browser.fetch_engagement_metrics(platform)

        # Calculate total engagement
        total_engagement = sum(metrics.values())

        # Generate learnings
        learnings = []
        if total_engagement > 100:
            learnings.append("High engagement - continue similar content style")
        elif total_engagement < 20:
            learnings.append("Low engagement - try different hooks or formatting")

        # Save to learning file
        learning_file = Path(config.get("learning.feedback_file", "~/.config/git-storyteller/learning.json")).expanduser()
        learning_file.parent.mkdir(parents=True, exist_ok=True)

        learning_data = {}
        if learning_file.exists():
            with open(learning_file) as f:
                learning_data = json.load(f)

        learning_data[platform] = learning_data.get(platform, {})
        learning_data[platform]["recent_metrics"] = metrics
        learning_data[platform]["total_engagement"] = total_engagement
        learning_data[platform]["learnings"] = learnings

        with open(learning_file, "w") as f:
            json.dump(learning_data, f, indent=2)

        return {
            "platform": platform,
            "metrics": metrics,
            "total_engagement": total_engagement,
            "learnings": learnings,
            "saved_to": str(learning_file),
        }

    except Exception as e:
        return {
            "platform": platform,
            "error": f"Failed to fetch engagement: {str(e)}",
        }


@mcp.tool()
async def autonomous_storyteller_workflow(
    target: str,
    platforms: list[str],
    template: str = "bento_metrics",
    ref: Optional[str] = None,
) -> dict:
    """Run the full autonomous storytelling workflow.

    This is the main tool that orchestrates the entire pipeline:
    1. Analyze repository/git commit
    2. Generate visual assets
    3. Create marketing copy
    4. Post to social platforms

    Args:
        target: Repository path or URL
        platforms: List of platforms to post to (["twitter"], ["linkedin"], or both)
        template: Visual template to use (default: "bento_metrics")
        ref: Optional git reference to analyze

    Returns:
        Dictionary with complete workflow results
    """
    try:
        results = {
            "steps": [],
            "success": True,
        }

        # Step 1: Analyze repository
        results["steps"].append({"step": "Analyzing repository...", "status": "running"})
        analysis = await analyze_repository_impact(target, ref=ref)

        if "error" in analysis:
            results["success"] = False
            results["steps"].append({"step": "Analysis failed", "status": "failed", "error": analysis["error"]})
            return results

        results["steps"].append({"step": "Analyzing repository...", "status": "completed", "result": analysis})

        # Step 2: Generate visual
        results["steps"].append({"step": "Generating visual asset...", "status": "running"})

        # Prepare data for template
        if template == "carbon_x":
            # Get latest commit for carbon_x
            latest_commit = analysis["recent_changes"][0] if analysis["recent_changes"] else {}
            visual_data = {
                "repo_name": analysis["name"],
                "commit_hash": latest_commit.get("hash", ""),
                "commit_message": latest_commit.get("message", ""),
                "files_changed": len(latest_commit.get("files_changed", [])),
                "additions": 0,  # Would need diff parsing
                "deletions": 0,
            }
        else:  # bento_metrics
            visual_data = {
                "repo_name": analysis["name"],
                "description": analysis["description"],
                "total_commits": analysis["total_commits"],
                "recent_count": len(analysis["recent_changes"]),
                "marketing_hooks": analysis["marketing_hooks"],
                "visual_highlights": analysis["visual_highlights"],
            }

        # Create temp file for image
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image_path = f.name

        render_result = await dynamic_template_render(
            template_name=template,
            data=visual_data,
            commit_hash=analysis["recent_changes"][0]["hash"] if analysis["recent_changes"] else None,
            output_path=image_path,
        )

        if not render_result.get("success"):
            results["success"] = False
            results["steps"].append({"step": "Render failed", "status": "failed", "error": render_result.get("error")})
            return results

        results["steps"].append({"step": "Generating visual asset...", "status": "completed", "image": image_path})

        # Step 3: Post to platforms
        for platform in platforms:
            results["steps"].append({"step": f"Posting to {platform}...", "status": "running"})

            # Generate caption
            caption = f"🚀 Just pushed updates to {analysis['name']}!\n\n"
            caption += "\n".join(analysis["marketing_hooks"][:3])

            post_result = await stealth_browser_dispatcher(
                platform=platform,
                text=caption,
                image_path=image_path,
            )

            results["steps"].append({
                "step": f"Posting to {platform}...",
                "status": "completed" if post_result["success"] else "failed",
                "result": post_result,
            })

        return results

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "steps": results.get("steps", []),
        }


def run_server():
    """Run the MCP server."""
    mcp.run()

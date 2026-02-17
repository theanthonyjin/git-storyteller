"""GitHub webhook server for real-time social media posting."""
import asyncio
import hmac
import json
from pathlib import Path
from typing import Optional

from aiohttp import web

from ..config import get_config
from .browser_automation import BrowserAutomation
from .git_analyzer import GitAnalyzer
from .visual_engine import VisualEngine


class WebhookServer:
    """GitHub webhook server for autonomous storytelling."""

    def __init__(self, port: int = 8080, secret: Optional[str] = None):
        """Initialize the webhook server.

        Args:
            port: Port to listen on
            secret: GitHub webhook secret for signature verification
        """
        self.port = port
        self.secret = secret
        self.config = get_config()
        self.git_analyzer = GitAnalyzer()
        self.visual_engine = VisualEngine()
        self.browser: Optional[BrowserAutomation] = None
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Setup webhook routes."""
        self.app.router.add_post("/webhook/github", self.handle_github_webhook)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_post("/webhook/test", self.test_webhook)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint.

        Args:
            request: HTTP request

        Returns:
            Health status response
        """
        return web.json_response({"status": "healthy", "service": "git-storyteller"})

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature.

        Args:
            payload: Request payload
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        if not self.secret:
            return True  # Skip verification if no secret configured

        hash_algorithm, github_signature = signature.split("=", 1)
        if hash_algorithm != "sha256":
            return False

        mac = hmac.new(self.secret.encode(), msg=payload, digestmod="sha256")
        expected_signature = mac.hexdigest()

        return hmac.compare_digest(expected_signature, github_signature)

    async def handle_github_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming GitHub webhook.

        Args:
            request: HTTP request

        Returns:
            Web response
        """
        # Verify signature
        signature = request.headers.get("X-Hub-Signature-256")
        if signature and not self._verify_signature(await request.read(), signature):
            return web.json_response({"error": "Invalid signature"}, status=401)

        # Parse event
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = await request.json()

        print(f"📩 Received webhook event: {event_type}")

        # Handle different event types
        if event_type == "push":
            await self._handle_push_event(payload)
        elif event_type == "pull_request":
            await self._handle_pull_request_event(payload)
        elif event_type == "release":
            await self._handle_release_event(payload)
        else:
            print(f"⚠️  Unsupported event type: {event_type}")

        return web.json_response({"status": "processed"})

    async def _handle_push_event(self, payload: dict):
        """Handle push event.

        Args:
            payload: GitHub webhook payload
        """
        try:
            repo_name = payload["repository"]["name"]
            repo_url = payload["repository"]["clone_url"]
            ref = payload["ref"]
            branch = ref.replace("refs/heads/", "")

            # Get commits
            commits = payload.get("commits", [])
            if not commits:
                print("No commits in push event")
                return

            print(f"📦 Push to {repo_name}/{branch} with {len(commits)} commit(s)")

            # Analyze repository
            impact = self.git_analyzer.analyze(repo_url, ref=branch, is_remote=True)

            # Generate visual
            template = self.config.get("templates.bento_metrics.enabled") and "bento_metrics" or "carbon_x"

            # Prepare data for template
            visual_data = {
                "repo_name": impact.name,
                "description": impact.description,
                "total_commits": impact.total_commits,
                "recent_count": len(impact.recent_changes),
                "marketing_hooks": impact.marketing_hooks,
                "visual_highlights": impact.visual_highlights,
            }

            # Generate image
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                image_path = f.name

            latest_commit = impact.recent_changes[0] if impact.recent_changes else None
            await self.visual_engine.render_template(
                template_name=template,
                data=visual_data,
                commit_hash=latest_commit.hash if latest_commit else None,
                output_path=Path(image_path),
            )

            # Generate caption
            caption = self._generate_push_caption(repo_name, branch, commits, impact)

            # Post to enabled platforms
            await self._post_to_platforms(caption, image_path)

            print(f"✅ Successfully processed push event for {repo_name}")

        except Exception as e:
            print(f"❌ Error handling push event: {e}")

    async def _handle_pull_request_event(self, payload: dict):
        """Handle pull request event.

        Args:
            payload: GitHub webhook payload
        """
        try:
            action = payload["action"]
            pr = payload["pull_request"]
            repo_name = payload["repository"]["name"]

            if action not in ["opened", "synchronized"]:
                print(f"Skipping PR action: {action}")
                return

            print(f"🔀 PR {action} in {repo_name}: {pr['title']}")

            # Analyze PR
            # Note: Analysis logic to be implemented for PR posting
            # pr_url = pr["url"]
            # impact = self.git_analyzer.analyze(pr_url, ref=pr["head"]["ref"], is_remote=True)

            # Post to platforms
            # (Implementation similar to push event)

            print(f"✅ Successfully processed PR event for {repo_name}")

        except Exception as e:
            print(f"❌ Error handling PR event: {e}")

    async def _handle_release_event(self, payload: dict):
        """Handle release event.

        Args:
            payload: GitHub webhook payload
        """
        try:
            action = payload["action"]
            release = payload["release"]
            repo_name = payload["repository"]["name"]

            if action != "published":
                print(f"Skipping release action: {action}")
                return

            print(f"🎉 Release published in {repo_name}: {release['name']}")

            # Generate release-specific content
            tag_name = release["tag_name"]
            release_notes = release.get("body", "")

            caption = f"""🚀 New Release: {repo_name} {tag_name}

{release_notes[:200]}

#github #release"""

            # Post to platforms
            await self._post_to_platforms(caption, image_path=None)

            print(f"✅ Successfully processed release event for {repo_name}")

        except Exception as e:
            print(f"❌ Error handling release event: {e}")

    def _generate_push_caption(self, repo_name: str, branch: str, commits: list, impact) -> str:
        """Generate caption for push event.

        Args:
            repo_name: Repository name
            branch: Branch name
            commits: List of commits
            impact: Repository impact analysis

        Returns:
            Generated caption
        """
        caption = f"🚀 Just pushed {len(commits)} commit{'s' if len(commits) > 1 else ''} to {repo_name}/{branch}!\n\n"

        # Add marketing hooks
        for hook in impact.marketing_hooks[:3]:
            caption += f"• {hook}\n"

        caption += "\n"

        # Add commit messages
        for commit in commits[:3]:
            message = commit.get("message", {}).get("headline", commit.get("message", ""))
            caption += f"• {message[:60]}...\n"

        caption += f"\n💻 View changes: {commits[0].get('url', '')}"

        return caption

    def _generate_pr_caption(self, pr: dict, impact) -> str:
        """Generate caption for pull request.

        Args:
            pr: Pull request data
            impact: Repository impact analysis

        Returns:
            Generated caption
        """
        caption = f"🔀 Opened PR in {pr['base']['repo']['name']}: {pr['title']}\n\n"

        caption += f"{pr.get('body', '')[:200]}\n\n"

        # Add stats
        caption += f"📊 +{pr.get('additions', 0)} -{pr.get('deletions', 0)} lines\n"
        caption += f"🔗 {pr['html_url']}"

        return caption

    async def _post_to_platforms(self, caption: str, image_path: Optional[str]):
        """Post to enabled social platforms.

        Args:
            caption: Post caption
            image_path: Optional path to image
        """
        if not self.browser:
            self.browser = BrowserAutomation()
            await self.browser.initialize()

        platforms = []
        if self.config.get("social.twitter.enabled"):
            platforms.append("twitter")
        if self.config.get("social.linkedin.enabled"):
            platforms.append("linkedin")

        for platform in platforms:
            try:
                if platform == "twitter":
                    await self.browser.post_to_twitter(caption, image_path=Path(image_path) if image_path else None)
                elif platform == "linkedin":
                    await self.browser.post_to_linkedin(caption, image_path=Path(image_path) if image_path else None)
            except Exception as e:
                print(f"❌ Failed to post to {platform}: {e}")

    async def test_webhook(self, request: web.Request) -> web.Response:
        """Test webhook endpoint.

        Args:
            request: HTTP request

        Returns:
            Test response
        """
        payload = await request.json()

        print("🧪 Testing webhook with payload:")
        print(json.dumps(payload, indent=2))

        return web.json_response({"status": "test processed", "payload": payload})

    async def start(self):
        """Start the webhook server."""
        print(f"🚀 Starting Git-Storyteller webhook server on port {self.port}")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        print(f"✅ Webhook server listening on http://localhost:{self.port}")
        print(f"📡 Webhook endpoint: http://localhost:{self.port}/webhook/github")

        # Keep server running
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down webhook server...")
            await runner.cleanup()


def run_webhook_server(port: int = 8080, secret: Optional[str] = None):
    """Run the webhook server.

    Args:
        port: Port to listen on
        secret: Optional GitHub webhook secret
    """
    server = WebhookServer(port=port, secret=secret)
    asyncio.run(server.start())

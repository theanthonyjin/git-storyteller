"""Visual rendering engine for creating beautiful code snapshots."""
import hashlib
from pathlib import Path
from typing import Optional

from jinja2 import Template
from playwright.async_api import async_playwright

from ..config import get_config


class VisualEngine:
    """Renders visual assets using HTML/CSS/JS."""

    def __init__(self):
        """Initialize the visual engine."""
        self.config = get_config()

    def generate_entropy_seed(self, commit_hash: str) -> float:
        """Generate entropy seed from commit hash.

        Args:
            commit_hash: Git commit hash

        Returns:
            Float value between 0 and 1
        """
        hash_bytes = hashlib.sha256(commit_hash.encode()).digest()
        return int.from_bytes(hash_bytes[:4], byteorder="big") / (2**32)

    async def render_template(
        self,
        template_name: str,
        data: dict,
        commit_hash: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> bytes:
        """Render a template to an image.

        Args:
            template_name: Name of the template (e.g., "carbon_x", "bento_metrics")
            data: Data to populate the template
            commit_hash: Optional commit hash for entropy seeding
            output_path: Optional path to save the image

        Returns:
            Image bytes
        """
        # Generate entropy seed if commit hash provided
        entropy = self.generate_entropy_seed(commit_hash or "default")

        # Load and render template
        template_html = self._load_template(template_name)
        rendered = template_html.render(
            **data,
            entropy=entropy,
            config=self.config.config,
        )

        # Take screenshot with Playwright
        screenshot = await self._screenshot_html(rendered, output_path)

        return screenshot

    def _load_template(self, template_name: str) -> Template:
        """Load a Jinja2 template.

        Args:
            template_name: Name of the template

        Returns:
            Jinja2 Template object
        """
        # This will be implemented when we create the actual templates
        # For now, return a basic template
        if template_name == "carbon_x":
            template_string = self._get_carbon_x_template()
        elif template_name == "bento_metrics":
            template_string = self._get_bento_metrics_template()
        else:
            template_string = "<html><body>{{ data }}</body></html>"

        return Template(template_string)

    async def _screenshot_html(self, html: str, output_path: Optional[Path] = None) -> bytes:
        """Take a screenshot of HTML content.

        Args:
            html: HTML content to screenshot
            output_path: Optional path to save the screenshot

        Returns:
            Image bytes
        """
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={"width": 1200, "height": 800},
                device_scale_factor=self.config.get("browser.screenshot_scale", 2.0),
            )

            # Set HTML content
            await page.set_content(html, wait_until="networkidle")

            # Take screenshot
            screenshot = await page.screenshot(
                type="png",
                path=str(output_path) if output_path else None,
                full_page=False,
            )

            await browser.close()

            return screenshot

    def _get_carbon_x_template(self) -> str:
        """Get the Carbon-X template HTML.

        Returns:
            HTML template string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, {{ config.primary_color }} 0%, #1a1a2e 100%);
            padding: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .carbon-container {
            background: rgba(0, 0, 0, {{ config.templates.carbon_x.background_opacity }});
            border-radius: {{ config.templates.carbon_x.border_radius }}px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            max-width: 1000px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .repo-name {
            font-size: 24px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 10px;
        }

        .commit-info {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
        }

        .commit-hash {
            color: {{ config.primary_color }};
            font-weight: 600;
        }

        .code-block {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 25px;
            overflow-x: auto;
            position: relative;
        }

        .code-block pre {
            font-size: 14px;
            line-height: 1.6;
            color: #e2e8f0;
        }

        .diff-add {
            color: #4ade80;
        }

        .diff-remove {
            color: #f87171;
        }

        .stats {
            display: flex;
            gap: 40px;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 600;
            color: {{ config.primary_color }};
        }

        .stat-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 5px;
        }

        .badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: {{ config.primary_color }};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="carbon-container">
        <div class="badge">🚀 Git-Storyteller</div>
        <div class="header">
            <div class="repo-name">{{ data.repo_name or 'Repository Update' }}</div>
            <div class="commit-info">
                <span class="commit-hash">{{ data.commit_hash[:8] }}</span>
                <span>{{ data.commit_message }}</span>
            </div>
        </div>

        {% if data.code_diff %}
        <div class="code-block">
            <pre>{{ data.code_diff }}</pre>
        </div>
        {% endif %}

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{ data.files_changed or 0 }}</div>
                <div class="stat-label">Files Changed</div>
            </div>
            <div class="stat">
                <div class="stat-value">+{{ data.additions or 0 }}</div>
                <div class="stat-label">Additions</div>
            </div>
            <div class="stat">
                <div class="stat-value">-{{ data.deletions or 0 }}</div>
                <div class="stat-label">Deletions</div>
            </div>
        </div>
    </div>
</body>
</html>
        """

    def _get_bento_metrics_template(self) -> str:
        """Get the Bento-Metrics template HTML.

        Returns:
            HTML template string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .bento-grid {
            display: grid;
            grid-template-columns: repeat({{ config.templates.bento_metrics.grid_columns }}, 1fr);
            gap: 20px;
            max-width: 1000px;
            width: 100%;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .card-large {
            grid-column: span 2;
        }

        .card-header {
            font-size: 14px;
            color: #64748b;
            margin-bottom: 15px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 48px;
            font-weight: 700;
            color: {{ config.primary_color }};
            margin-bottom: 5px;
        }

        .metric-label {
            font-size: 16px;
            color: #475569;
        }

        .hook-item {
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }

        .hook-item:last-child {
            border-bottom: none;
        }

        .hook-text {
            font-size: 18px;
            color: #1e293b;
            font-weight: 600;
        }

        .trend-indicator {
            display: inline-block;
            padding: 4px 12px;
            background: #dcfce7;
            color: #166534;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-top: 10px;
        }

        .visual-highlight {
            background: linear-gradient(135deg, {{ config.primary_color }} 0%, #8b5cf6 100%);
            color: white;
        }

        .visual-highlight .card-header {
            color: rgba(255, 255, 255, 0.8);
        }

        .visual-highlight .metric-value {
            color: white;
        }

        .visual-highlight .metric-label {
            color: rgba(255, 255, 255, 0.9);
        }
    </style>
</head>
<body>
    <div class="bento-grid">
        <div class="card card-large visual-highlight">
            <div class="card-header">Repository</div>
            <div class="metric-value">{{ data.repo_name or 'Project' }}</div>
            <div class="metric-label">{{ data.description or 'Building something awesome' }}</div>
            <div class="trend-indicator">🚀 Active Development</div>
        </div>

        <div class="card">
            <div class="card-header">Total Commits</div>
            <div class="metric-value">{{ data.total_commits }}</div>
            <div class="metric-label">All time</div>
        </div>

        <div class="card">
            <div class="card-header">Recent Changes</div>
            <div class="metric-value">{{ data.recent_count }}</div>
            <div class="metric-label">Last 24 hours</div>
        </div>

        <div class="card card-large">
            <div class="card-header">Marketing Hooks</div>
            {% for hook in data.marketing_hooks %}
            <div class="hook-item">
                <div class="hook-text">{{ hook }}</div>
            </div>
            {% endfor %}
        </div>

        {% if data.visual_highlights %}
        <div class="card card-large">
            <div class="card-header">Highlights</div>
            {% for highlight in data.visual_highlights %}
            <div class="hook-item">
                <div class="hook-text">{{ highlight }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
        """

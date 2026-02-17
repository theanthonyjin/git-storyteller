# 🧙‍♂️ Git-Storyteller

> **Stop coding in silence. Turn commits into viral updates.**

Git-Storyteller is an AI-native marketing agent **for developers**, powered by the [MCP (Model Context Protocol)](https://modelcontextprotocol.io/). It understands the deep semantics of your code changes, generates high-fidelity visual assets with an "Engineering Aesthetic," and autonomously distributes updates across social platforms.

## ✨ Key Features

- **🤖 Autonomous Semantic Analysis**: Go beyond boring diffs. The AI interprets your logic to explain how much memory you saved or what a new feature means for your users.
- **🎨 Deterministic Rendering**: Say goodbye to "AI Slop." We use code-based rendering to create minimalist visual assets inspired by Linear/Stripe aesthetics.
- **🚀 God Mode (Autonomous by Default)**: Push code, get tweets. It reuses your local browser session to ensure security and zero-click distribution.
- **🔌 MCP Powered**: Designed to live inside your AI workflows, perfectly compatible with Claude Desktop and Cursor.

## 📦 Installation

```bash
pip install git-storyteller
```

### 🛠️ Configure MCP (Claude Desktop)

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "git-storyteller": {
      "command": "python",
      "args": ["-m", "git_storyteller"]
    }
  }
}
```

## 🎯 Usage

### Basic Workflow

```
1. Code something amazing
2. Commit your changes
3. Ask Claude: "Turn my recent commits into a viral tweet"
4. Git-Storyteller analyzes, generates visuals, and posts automatically
```

### MCP Tools

Git-Storyteller provides several MCP tools:

#### `analyze_repository_impact`

Analyze a local or remote repository for marketing value.

```python
analyze_repository_impact(
    target="/path/to/repo",  # or "https://github.com/user/repo"
    ref="main"  # optional: branch, commit, or PR
)
```

#### `summarize_milestone_impact`

Summarize cumulative impact over a time period (e.g., "What I built today").

```python
summarize_milestone_impact(
    target="/path/to/repo",
    hours=24  # look back 24 hours
)
```

#### `dynamic_template_render`

Render a visual template with data-driven styling.

```python
dynamic_template_render(
    template_name="bento_metrics",  # or "carbon_x"
    data={"repo_name": "My Project", "total_commits": 100},
    commit_hash="abc123",  # for entropy seeding
    output_path="./output.png"
)
```

#### `stealth_browser_dispatcher`

Dispatch a social media post with stealth automation.

```python
stealth_browser_dispatcher(
    platform="twitter",  # or "linkedin"
    text="🚀 Just shipped a new feature!",
    image_path="./output.png",
    scheduled_at="09:00"  # optional: schedule for specific time
)
```

#### `fetch_engagement_feedback`

Fetch engagement metrics from recent posts for learning.

```python
fetch_engagement_feedback(
    platform="twitter",
    limit=5
)
```

#### `autonomous_storyteller_workflow`

Run the full autonomous storytelling workflow.

```python
autonomous_storyteller_workflow(
    target="/path/to/repo",
    platforms=["twitter", "linkedin"],
    template="bento_metrics"
)
```

## 🎨 Visual Templates

### Carbon-X

Minimalist code snapshots with JetBrains Mono font and automatic diff highlighting. Perfect for showcasing specific code changes.

### Bento-Metrics

Grid-based dashboard inspired by Apple's marketing materials. Great for showing overall progress and metrics.

## ⚙️ Configuration

Create `~/.config/git-storyteller/config.yaml`:

```yaml
# Mode: autonomous or semi-auto
mode: autonomous

# Theme settings
theme: dark  # dark or light
primary_color: "#6366f1"
brand_colors:
  - "#6366f1"
  - "#8b5cf6"
  - "#a855f7"

# Template settings
templates:
  carbon_x:
    enabled: true
    background_opacity: 0.95
    border_radius: 12
  bento_metrics:
    enabled: true
    grid_columns: 3

# Browser settings
browser:
  user_data_dir: null  # Uses default Chrome profile
  headless: false
  screenshot_scale: 2.0  # High-res screenshots

# Social platforms
social:
  twitter:
    enabled: true
    scheduled_at: "09:00"  # Schedule posts for 9 AM
  linkedin:
    enabled: false

# Entropy settings (for stealth)
entropy:
  temperature: 0.8
  randomize_timing: true
  min_wait_seconds: 8.4
  max_wait_seconds: 22.1

# Learning settings
learning:
  feedback_file: "~/.config/git-storyteller/learning.json"
```

## ✨ Current Features

**Core Capabilities:**
- AST-based code semantic parser
- GitHub remote repository clone and analysis
- Playwright browser automation with Chrome profile reuse
- Configurable CSS templates (Carbon-X, Bento-Metrics)

**Automation & Integration:**
- GitHub Webhook integration for real-time posting
- GitHub Action workflows for automatic triggers
- Feedback learning system based on historical data
- Self-hype amplification (reply to posts for extended reach)

**Analytics & Optimization:**
- Engagement metrics tracking (likes, retweets, replies)
- Performance analytics by hook type and template
- Content suggestions based on historical data
- MCP ecosystem visibility (glama.ai)

**Coming Soon:**
- Multi-platform support (Mastodon, Bluesky, Threads)
- A/B testing for content optimization
- Team collaboration features
- Advanced analytics dashboard

## 🔄 Webhook Server

Git-Storyteller includes a webhook server for real-time social media posting:

```bash
# Start webhook server on port 8080
git-storyteller webhook 8080
```

Configure your GitHub repository webhooks to point to:
```
https://your-server.com:8080/webhook/github
```

Supported events:
- `push` - Automatic posting on code pushes
- `pull_request` - PR announcements
- `release` - Release notifications

## 🧠 Learning & Insights

View learning insights and performance analytics:

```bash
git-storyteller insights
```

The learning system tracks:
- Engagement metrics (likes, retweets, replies)
- Best performing hooks and templates
- Optimal posting times
- Content suggestions based on historical data

## 📈 Self-Hype Amplification

Amplify your content with automated follow-up replies:

- **Smart Replies**: Post follow-up content 2-4 hours after original post
- **Thread Creation**: Build threads from related content
- **Engagement-Based**: Amplify based on initial engagement metrics
- **Multiple Strategies**: Choose from insight, teaser, question, or thread replies

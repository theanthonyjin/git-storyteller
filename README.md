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

### 🚀 Quick Start (Try it now!)

```bash
# 1. Install Playwright browsers (one-time setup)
playwright install chromium

# 2. Log into Twitter/X in your browser

# 3. Run in confirm mode to see it in action
python scripts/analyze_and_tweet.py --confirm

# 4. Review the tweet and image, then press 'y' to post!
```

**What happens:**
- 🔍 Analyzes your recent commits
- 🎨 Generates a professional image
- 📝 Writes engaging tweet content
- 👀 Shows you a preview
- ⚠️ Asks for your approval
- 🐦 Posts to Twitter when you say yes!

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

### Command Line Interface

The easiest way to use Git-Storyteller is via the command-line script:

```bash
# Confirm Mode (Recommended) - Preview and approve before posting
python scripts/analyze_and_tweet.py --confirm

# Test Mode - Preview only, no posting
python scripts/analyze_and_tweet.py --test

# Auto Mode - Posts automatically without confirmation
python scripts/analyze_and_tweet.py

# Analyze a specific repository
python scripts/analyze_and_tweet.py --confirm --repo /path/to/repo
```

#### Confirm Mode Details

**Recommended for first-time users!** Confirm mode gives you full control:

1. ✅ **Analyzes your repository** - Shows commit history and impact
2. ✅ **Generates visual asset** - Creates a professional image
3. ✅ **Crafts tweet content** - Writes engaging copy based on your changes
4. ✅ **Shows you the preview** - Displays the tweet and image
5. ⚠️ **Asks for confirmation** - You decide whether to post

```
============================================================
  ⚠️  CONFIRMATION REQUIRED
============================================================

Options:
  [y] Yes - Post to Twitter now
  [s] Save - Save content without posting
  [n] No - Cancel and exit

============================================================

Post to Twitter? (y/s/n):
```

**What happens in each mode:**
- **[y] Yes** - Opens browser with your Twitter session, posts the tweet with image
- **[s] Save** - Saves the tweet text and image to `output/` folder, no posting
- **[n] No** - Cancels without posting

**Files saved in `output/` directory:**
- `tweet_visual.png` - Generated image asset
- `tweet_content.txt` - Tweet text content

### Basic Workflow

```
1. Code something amazing
2. Commit your changes
3. Run: python scripts/analyze_and_tweet.py --confirm
4. Review the generated tweet and image
5. Press 'y' to post, 's' to save, or 'n' to cancel
4. Git-Storyteller posts to Twitter using your browser session
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

### Browser Setup (Required for Posting)

Git-Storyteller uses your existing browser session to post to Twitter. This is more secure than API keys because:

- ✅ **No API credentials stored** - Uses your logged-in session
- ✅ **Familiar interface** - You see exactly what's being posted
- ✅ **Full control** - Confirm mode shows you before posting
- ✅ **Session reuse** - Your cookies and auth are already there

**Before first use:**
1. Install Playwright browsers: `playwright install chromium`
2. Log into Twitter/X in your Chrome browser
3. Run Git-Storyteller in confirm mode first

### Configuration File

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

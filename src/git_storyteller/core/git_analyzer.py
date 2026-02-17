"""Git repository analyzer for understanding code semantics."""
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import git
from tree_sitter import Language, Parser


@dataclass
class CommitInfo:
    """Information about a git commit."""

    hash: str
    author: str
    message: str
    date: str
    files_changed: List[str]
    diff_summary: str
    semantic_impact: str


@dataclass
class RepositoryImpact:
    """Analysis of repository marketing value."""

    name: str
    description: str
    recent_changes: List[CommitInfo]
    total_commits: int
    marketing_hooks: List[str]
    visual_highlights: List[str]


class GitAnalyzer:
    """Analyzes git repositories for marketing impact."""

    def __init__(self):
        """Initialize the git analyzer."""
        self.parser = Parser()
        self._init_languages()

    def _init_languages(self):
        """Initialize tree-sitter language parsers."""
        # Try to load common languages
        try:
            # Python
            PY_LANGUAGE = Language.build_library(
                # Build in a temporary directory
                str(Path(tempfile.gettempdir()) / "tree-sitter-languages.so"),
                [
                    "https://github.com/tree-sitter/tree-sitter-python",
                    "https://github.com/tree-sitter/tree-sitter-javascript",
                    "https://github.com/tree-sitter/tree-sitter-typescript",
                ],
            )
            self.parser.set_language(Language(PY_LANGUAGE, "python"))
        except Exception as e:
            print(f"Warning: Could not initialize tree-sitter: {e}")

    def analyze(
        self, target: str, ref: Optional[str] = None, is_remote: bool = False
    ) -> RepositoryImpact:
        """Analyze a local or remote git repository.

        Args:
            target: Local path or GitHub URL
            ref: Commit hash, branch, or PR reference
            is_remote: Whether target is a remote URL

        Returns:
            RepositoryImpact analysis
        """
        repo = self._get_repo(target, is_remote)
        return self._analyze_repo(repo, ref)

    def _get_repo(self, target: str, is_remote: bool) -> git.Repo:
        """Get git.Repo object from path or URL.

        Args:
            target: Local path or GitHub URL
            is_remote: Whether target is a remote URL

        Returns:
            git.Repo object
        """
        if is_remote:
            # Shallow clone for remote URLs
            temp_dir = tempfile.mkdtemp(prefix="git-storyteller-")
            print(f"Cloning {target} to {temp_dir}...")
            repo = git.Repo.clone_from(target, temp_dir, depth=1)
            return repo
        else:
            return git.Repo(target)

    def _analyze_repo(self, repo: git.Repo, ref: Optional[str] = None) -> RepositoryImpact:
        """Analyze repository for marketing impact.

        Args:
            repo: Git repository object
            ref: Optional commit/branch reference

        Returns:
            RepositoryImpact analysis
        """
        # Get repository name
        repo_name = Path(repo.working_dir).name

        # Get recent commits
        if ref:
            try:
                commits = list(repo.iter_commits(ref, max_count=10))
            except Exception:
                commits = list(repo.iter_commits(max_count=10))
        else:
            commits = list(repo.iter_commits(max_count=10))

        # Analyze commits
        commit_infos = []
        for commit in commits:
            commit_info = CommitInfo(
                hash=commit.hexsha[:8],
                author=commit.author.name,
                message=commit.message.strip(),
                date=commit.committed_datetime.isoformat(),
                files_changed=[item.a_path for item in commit.diff()],
                diff_summary=self._get_diff_summary(commit),
                semantic_impact=self._analyze_semantic_impact(commit),
            )
            commit_infos.append(commit_info)

        # Generate marketing hooks
        marketing_hooks = self._generate_marketing_hooks(commit_infos)

        # Generate visual highlights
        visual_highlights = self._generate_visual_highlights(commit_infos)

        return RepositoryImpact(
            name=repo_name,
            description=self._get_repo_description(repo),
            recent_changes=commit_infos,
            total_commits=sum(1 for _ in repo.iter_commits()),
            marketing_hooks=marketing_hooks,
            visual_highlights=visual_highlights,
        )

    def _get_diff_summary(self, commit: git.Commit) -> str:
        """Get a summary of the commit diff.

        Args:
            commit: Git commit object

        Returns:
            Diff summary string
        """
        diff = commit.diff()
        if not diff:
            return "No changes"

        additions = sum(d.diff.count(b"+") if d.diff else 0 for d in diff)
        deletions = sum(d.diff.count(b"-") if d.diff else 0 for d in diff)
        files = len(diff)

        return f"{files} file(s) changed, {additions} insertions(+), {deletions} deletions(-)"

    def _analyze_semantic_impact(self, commit: git.Commit) -> str:
        """Analyze the semantic impact of a commit.

        Args:
            commit: Git commit object

        Returns:
            Semantic impact description
        """
        message = commit.message.strip().lower()

        # Categorize commit type
        if any(word in message for word in ["fix", "bug", "patch"]):
            return "Bug fix - Improved stability and fixed issues"
        elif any(word in message for word in ["feat", "add", "new"]):
            return "Feature - Added new functionality"
        elif any(word in message for word in ["refactor", "clean", "improve"]):
            return "Refactor - Code quality improvements"
        elif any(word in message for word in ["perf", "optimize", "speed"]):
            return "Performance - Optimized for better performance"
        elif any(word in message for word in ["doc", "readme"]):
            return "Documentation - Updated documentation"
        elif any(word in message for word in ["test", "spec"]):
            return "Testing - Improved test coverage"
        else:
            return "Update - General code changes"

    def _generate_marketing_hooks(self, commits: List[CommitInfo]) -> List[str]:
        """Generate marketing hooks from commits.

        Args:
            commits: List of commit information

        Returns:
            List of marketing hook strings
        """
        hooks = []

        # Count different types of changes
        feat_count = sum(1 for c in commits if "feature" in c.semantic_impact.lower())
        fix_count = sum(1 for c in commits if "bug fix" in c.semantic_impact.lower())
        perf_count = sum(1 for c in commits if "performance" in c.semantic_impact.lower())

        if feat_count > 0:
            hooks.append(f"🚀 {feat_count} new feature{'s' if feat_count > 1 else ''} shipped")
        if fix_count > 0:
            hooks.append(f"🐛 {fix_count} bug{'s' if fix_count > 1 else ''} squashed")
        if perf_count > 0:
            hooks.append(f"⚡ Performance improvements across {perf_count} component{'s' if perf_count > 1 else ''}")

        if not hooks:
            hooks.append(f"💪 {len(commits)} commits pushing the codebase forward")

        return hooks

    def generate_sexy_tweet_content(self, impact: 'RepositoryImpact', repo_url: str = None) -> str:
        """Generate compelling, sexy tweet content that summarizes actual changes.

        Args:
            impact: RepositoryImpact analysis
            repo_url: Optional repository URL to include in tweet

        Returns:
            Compelling tweet content
        """
        # Extract actual, specific changes from commit messages
        recent = impact.recent_changes[:3]
        real_changes = []

        for commit in recent:
            msg = commit.message.lower()

            # Only extract REAL, specific functionality changes (not infrastructure/tooling)
            if 'mcp' in msg:
                real_changes.append("🔌 MCP integration")
            elif 'browser' in msg or 'playwright' in msg:
                real_changes.append("🎭 Browser automation")
            elif 'visual' in msg or 'template' in msg:
                real_changes.append("🎨 Visual rendering")
            elif 'api' in msg:
                real_changes.append("🌐 API endpoints")
            elif 'auth' in msg:
                real_changes.append("🔐 Authentication")
            elif 'database' in msg or 'db' in msg:
                real_changes.append("🗄️ Database layer")
            elif 'ui' in msg or 'frontend' in msg:
                real_changes.append("💄 UI improvements")
            elif 'chat' in msg or 'message' in msg:
                real_changes.append("💬 Chat features")
            elif 'search' in msg:
                real_changes.append("🔍 Search functionality")
            elif 'export' in msg or 'download' in msg:
                real_changes.append("📥 Export features")

        # Remove duplicates while preserving order
        seen = set()
        unique_changes = []
        for change in real_changes:
            if change not in seen:
                seen.add(change)
                unique_changes.append(change)

        # Build the tweet - eyecatching style
        tweet_lines = []

        # Hook - make it punchy and eyecatching
        if impact.total_commits <= 5:
            tweet_lines.append(f"🚀 {impact.name} v1.0 is LIVE")
        else:
            tweet_lines.append(f"🔥 {impact.name} just got an upgrade")

        tweet_lines.append("")

        # What it does - single line
        tweet_lines.append("Turn commits into viral updates with AI-powered marketing automation.")

        tweet_lines.append("")

        # Real technical changes only (no generic fluff)
        if unique_changes:
            # Show only the first/most important change
            tweet_lines.append(unique_changes[0])
        elif len(recent) == 1:
            # Use actual commit message if no specific pattern matched
            msg = recent[0].message
            # Clean up the message
            for prefix in ['add:', 'fix:', 'feat:', 'chore:']:
                msg = msg.replace(prefix, '', 1).strip()
            tweet_lines.append(f"💡 {msg[:80]}")

        # Hashtags - make them pop
        tweet_lines.append("")
        tweet_lines.append("👇")

        # Add repo link if provided
        if repo_url:
            tweet_lines.append(f"🔗 {repo_url}")

        tweet_lines.append("#DevTools #AI #OpenSource")

        return "\n".join(tweet_lines)

    @staticmethod
    def get_last_tweeted_commit(history_file: Path = None) -> str:
        """Get the last commit hash that was tweeted.

        Args:
            history_file: Path to history file (default: output/.tweeted_history)

        Returns:
            Last commit hash or empty string if none
        """
        if history_file is None:
            history_file = Path.cwd() / "output" / ".tweeted_history"

        if history_file.exists():
            with open(history_file, 'r') as f:
                return f.read().strip()
        return ""

    @staticmethod
    def save_tweeted_commit(commit_hash: str, history_file: Path = None):
        """Save the commit hash that was just tweeted.

        Args:
            commit_hash: Commit hash to save
            history_file: Path to history file (default: output/.tweeted_history)
        """
        if history_file is None:
            history_file = Path.cwd() / "output" / ".tweeted_history"

        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, 'w') as f:
            f.write(commit_hash)

    def get_new_commits(self, repo: git.Repo, last_tweeted: str = None) -> list:
        """Get commits since the last tweeted one.

        Args:
            repo: Git repository object
            last_tweeted: Last commit hash that was tweeted

        Returns:
            List of new commits
        """
        if not last_tweeted:
            # No history, get recent commits
            return list(repo.iter_commits(max_count=10))

        # Get commits since last tweeted
        commits = []
        for commit in repo.iter_commits():
            if commit.hexsha.startswith(last_tweeted):
                break
            commits.append(commit)
        return commits[:10]  # Limit to 10

    def _generate_visual_highlights(self, commits: List[CommitInfo]) -> List[str]:
        """Generate visual highlights for templates.

        Args:
            commits: List of commit information

        Returns:
            List of visual highlight strings
        """
        highlights = []

        # Find files with most changes
        file_counts = {}
        for commit in commits:
            for file_path in commit.files_changed:
                file_counts[file_path] = file_counts.get(file_path, 0) + 1

        if file_counts:
            top_file = max(file_counts, key=file_counts.get)
            highlights.append(f"Most active file: {top_file}")

        # Check for significant commits
        for commit in commits[:3]:
            if any(word in commit.message.lower() for word in ["major", "breaking", "rewrite"]):
                highlights.append(f"🔥 Breaking change: {commit.message[:50]}...")
                break

        return highlights[:3]  # Limit to 3 highlights

    def _get_repo_description(self, repo: git.Repo) -> str:
        """Get repository description from README or similar.

        Args:
            repo: Git repository object

        Returns:
            Repository description
        """
        readme_paths = ["README.md", "README.txt", "README"]
        for readme in readme_paths:
            readme_path = Path(repo.working_dir) / readme
            if readme_path.exists():
                try:
                    with open(readme_path) as f:
                        first_line = f.readline().strip()
                        # Skip title lines
                        if first_line.startswith("#"):
                            first_line = f.readline().strip()
                        return first_line[:200]
                except Exception:
                    pass

        return "A software development repository"

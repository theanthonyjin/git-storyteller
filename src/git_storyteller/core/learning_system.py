"""Feedback learning system for optimizing content generation."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..config import get_config


class EngagementMetrics:
    """Engagement metrics for a post."""

    def __init__(self, likes: int = 0, retweets: int = 0, replies: int = 0, views: int = 0):
        """Initialize engagement metrics.

        Args:
            likes: Number of likes
            retweets: Number of retweets/shares
            replies: Number of replies/comments
            views: Number of views/impressions
        """
        self.likes = likes
        self.retweets = retweets
        self.replies = replies
        self.views = views

    @property
    def total_engagement(self) -> int:
        """Calculate total engagement score.

        Returns:
            Total engagement score
        """
        return self.likes + (self.retweets * 2) + (self.replies * 3)

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate.

        Returns:
            Engagement rate as percentage (0-100)
        """
        if self.views == 0:
            return 0.0
        return (self.total_engagement / self.views) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "likes": self.likes,
            "retweets": self.retweets,
            "replies": self.replies,
            "views": self.views,
            "total_engagement": self.total_engagement,
            "engagement_rate": self.engagement_rate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EngagementMetrics":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            EngagementMetrics instance
        """
        return cls(
            likes=data.get("likes", 0),
            retweets=data.get("retweets", 0),
            replies=data.get("replies", 0),
            views=data.get("views", 0),
        )


class PostRecord:
    """Record of a social media post."""

    def __init__(
        self,
        post_id: str,
        platform: str,
        content: str,
        hook_type: str,
        template: str,
        timestamp: str,
        metrics: Optional[EngagementMetrics] = None,
    ):
        """Initialize post record.

        Args:
            post_id: Unique post identifier
            platform: Platform posted to (twitter, linkedin)
            content: Post content
            hook_type: Type of hook used (e.g., "feature", "bug_fix", "milestone")
            template: Template used (carbon_x, bento_metrics)
            timestamp: ISO timestamp of post
            metrics: Optional engagement metrics
        """
        self.post_id = post_id
        self.platform = platform
        self.content = content
        self.hook_type = hook_type
        self.template = template
        self.timestamp = timestamp
        self.metrics = metrics or EngagementMetrics()

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "post_id": self.post_id,
            "platform": self.platform,
            "content": self.content,
            "hook_type": self.hook_type,
            "template": self.template,
            "timestamp": self.timestamp,
            "metrics": self.metrics.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PostRecord":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            PostRecord instance
        """
        return cls(
            post_id=data["post_id"],
            platform=data["platform"],
            content=data["content"],
            hook_type=data["hook_type"],
            template=data["template"],
            timestamp=data["timestamp"],
            metrics=EngagementMetrics.from_dict(data.get("metrics", {})),
        )


class LearningSystem:
    """Learning system for optimizing content generation."""

    def __init__(self):
        """Initialize the learning system."""
        self.config = get_config()
        self.learning_file = Path(self.config.get("learning.feedback_file")).expanduser()
        self.data = self._load_learning_data()

    def _load_learning_data(self) -> dict:
        """Load learning data from file.

        Returns:
            Learning data dictionary
        """
        if not self.learning_file.exists():
            return {
                "posts": [],
                "hook_performance": {},
                "template_performance": {},
                "best_practices": [],
                "last_updated": None,
            }

        try:
            with open(self.learning_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load learning data: {e}")
            return {}

    def _save_learning_data(self):
        """Save learning data to file."""
        self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        self.data["last_updated"] = datetime.now().isoformat()

        with open(self.learning_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def record_post(
        self,
        post_id: str,
        platform: str,
        content: str,
        hook_type: str,
        template: str,
    ) -> PostRecord:
        """Record a new post.

        Args:
            post_id: Unique post identifier
            platform: Platform posted to
            content: Post content
            hook_type: Type of hook used
            template: Template used

        Returns:
            PostRecord instance
        """
        timestamp = datetime.now().isoformat()
        record = PostRecord(
            post_id=post_id,
            platform=platform,
            content=content,
            hook_type=hook_type,
            template=template,
            timestamp=timestamp,
        )

        self.data["posts"].append(record.to_dict())
        self._save_learning_data()

        return record

    def update_metrics(self, post_id: str, metrics: EngagementMetrics):
        """Update metrics for a post.

        Args:
            post_id: Post identifier
            metrics: New engagement metrics
        """
        for post in self.data["posts"]:
            if post["post_id"] == post_id:
                post["metrics"] = metrics.to_dict()
                self._update_performance_stats()
                self._save_learning_data()
                return

        print(f"Warning: Post {post_id} not found")

    def _update_performance_stats(self):
        """Update performance statistics."""
        # Calculate hook performance
        hook_stats = {}
        for post in self.data["posts"]:
            hook = post["hook_type"]
            if hook not in hook_stats:
                hook_stats[hook] = {"total_engagement": 0, "count": 0}

            metrics = post.get("metrics", {})
            total = metrics.get("total_engagement", 0)
            hook_stats[hook]["total_engagement"] += total
            hook_stats[hook]["count"] += 1

        # Calculate averages
        self.data["hook_performance"] = {}
        for hook, stats in hook_stats.items():
            if stats["count"] > 0:
                avg = stats["total_engagement"] / stats["count"]
                self.data["hook_performance"][hook] = {
                    "avg_engagement": avg,
                    "post_count": stats["count"],
                }

        # Calculate template performance
        template_stats = {}
        for post in self.data["posts"]:
            template = post["template"]
            if template not in template_stats:
                template_stats[template] = {"total_engagement": 0, "count": 0}

            metrics = post.get("metrics", {})
            total = metrics.get("total_engagement", 0)
            template_stats[template]["total_engagement"] += total
            template_stats[template]["count"] += 1

        self.data["template_performance"] = {}
        for template, stats in template_stats.items():
            if stats["count"] > 0:
                avg = stats["total_engagement"] / stats["count"]
                self.data["template_performance"][template] = {
                    "avg_engagement": avg,
                    "post_count": stats["count"],
                }

    def get_best_hook_type(self) -> Optional[str]:
        """Get the best performing hook type.

        Returns:
            Best hook type or None
        """
        if not self.data["hook_performance"]:
            return None

        return max(
            self.data["hook_performance"].items(),
            key=lambda x: x[1]["avg_engagement"],
        )[0]

    def get_best_template(self) -> Optional[str]:
        """Get the best performing template.

        Returns:
            Best template or None
        """
        if not self.data["template_performance"]:
            return None

        return max(
            self.data["template_performance"].items(),
            key=lambda x: x[1]["avg_engagement"],
        )[0]

    def get_hook_suggestions(self, limit: int = 5) -> List[str]:
        """Get hook suggestions based on performance.

        Args:
            limit: Maximum number of suggestions

        Returns:
            List of hook suggestions
        """
        # Find posts with highest engagement
        sorted_posts = sorted(
            self.data["posts"],
            key=lambda p: p.get("metrics", {}).get("total_engagement", 0),
            reverse=True,
        )

        suggestions = []
        for post in sorted_posts[:limit]:
            content = post.get("content", "")
            # Extract hook (first line or first sentence)
            lines = content.split("\n")
            hook = lines[0] if lines else content[:100]
            suggestions.append(hook)

        return suggestions

    def optimize_prompt(self, base_prompt: str) -> str:
        """Optimize a prompt based on learning data.

        Args:
            base_prompt: Base prompt to optimize

        Returns:
            Optimized prompt
        """
        # Add best practices to prompt
        best_hooks = self.get_hook_suggestions(3)

        if best_hooks:
            base_prompt += "\n\nHere are some high-performing hook examples:\n"
            for i, hook in enumerate(best_hooks, 1):
                base_prompt += f"{i}. {hook}\n"

        # Suggest best template
        best_template = self.get_best_template()
        if best_template:
            base_prompt += f"\nRecommended template: {best_template} (based on historical performance)\n"

        # Suggest best hook type
        best_hook = self.get_best_hook_type()
        if best_hook:
            base_prompt += f"Recommended hook type: {best_hook} (based on historical performance)\n"

        return base_prompt

    def get_recent_posts(self, days: int = 7) -> List[PostRecord]:
        """Get posts from the last N days.

        Args:
            days: Number of days to look back

        Returns:
            List of recent posts
        """
        cutoff = datetime.now() - timedelta(days=days)

        recent = []
        for post_data in self.data["posts"]:
            timestamp = datetime.fromisoformat(post_data["timestamp"])
            if timestamp >= cutoff:
                recent.append(PostRecord.from_dict(post_data))

        return recent

    def get_insights(self) -> dict:
        """Get insights from learning data.

        Returns:
            Insights dictionary
        """
        total_posts = len(self.data["posts"])
        if total_posts == 0:
            return {"message": "No data yet. Start posting to gather insights!"}

        # Calculate total engagement
        total_engagement = sum(
            p.get("metrics", {}).get("total_engagement", 0) for p in self.data["posts"]
        )

        # Average engagement
        avg_engagement = total_engagement / total_posts if total_posts > 0 else 0

        # Best performing posts
        top_posts = sorted(
            self.data["posts"],
            key=lambda p: p.get("metrics", {}).get("total_engagement", 0),
            reverse=True,
        )[:3]

        return {
            "total_posts": total_posts,
            "total_engagement": total_engagement,
            "avg_engagement": avg_engagement,
            "best_hook_type": self.get_best_hook_type(),
            "best_template": self.get_best_template(),
            "hook_performance": self.data.get("hook_performance", {}),
            "template_performance": self.data.get("template_performance", {}),
            "top_posts": [
                {"content": p["content"][:100], "engagement": p.get("metrics", {}).get("total_engagement", 0)}
                for p in top_posts
            ],
        }

    def export_learning_data(self) -> str:
        """Export learning data as JSON string.

        Returns:
            JSON string of learning data
        """
        return json.dumps(self.data, indent=2)

    def import_learning_data(self, data: str):
        """Import learning data from JSON string.

        Args:
            data: JSON string
        """
        self.data = json.loads(data)
        self._save_learning_data()

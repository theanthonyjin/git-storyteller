"""Configuration management for git-storyteller."""
import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Configuration manager for git-storyteller."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration.

        Args:
            config_path: Optional path to config.yaml file. If not provided,
                        looks in ~/.config/git-storyteller/config.yaml
        """
        if config_path is None:
            config_path = Path.home() / ".config" / "git-storyteller" / "config.yaml"

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary with defaults
        """
        defaults = {
            "mode": "autonomous",  # autonomous or semi-auto
            "theme": "dark",  # dark or light
            "primary_color": "#6366f1",
            "brand_colors": ["#6366f1", "#8b5cf6", "#a855f7"],
            "logo_path": None,
            "font_family": "JetBrains Mono",
            "templates": {
                "carbon_x": {
                    "enabled": True,
                    "background_opacity": 0.95,
                    "border_radius": 12,
                },
                "bento_metrics": {
                    "enabled": True,
                    "grid_columns": 3,
                },
            },
            "browser": {
                "user_data_dir": None,  # Defaults to Chrome's default profile
                "headless": False,
                "screenshot_scale": 2.0,  # For high-res screenshots
            },
            "social": {
                "twitter": {
                    "enabled": False,
                    "scheduled_at": None,  # "09:00" for 9 AM
                },
                "linkedin": {
                    "enabled": False,
                },
            },
            "entropy": {
                "temperature": 0.8,
                "randomize_timing": True,
                "min_wait_seconds": 8.4,
                "max_wait_seconds": 22.1,
            },
            "learning": {
                "feedback_file": "~/.config/git-storyteller/learning.json",
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                    return self._merge_config(defaults, user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration.")

        return defaults

    def _merge_config(self, base: dict, override: dict) -> dict:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Merged configuration
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default=None):
        """Get configuration value by dot-separated key.

        Args:
            key: Dot-separated configuration key (e.g., 'browser.headless')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def save(self):
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance.

    Returns:
        Configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config

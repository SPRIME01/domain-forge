"""Plugin configuration management."""

from pathlib import Path
from typing import Dict, Any
import yaml
from dataclasses import dataclass, asdict


@dataclass
class PluginConfig:
    """Configuration for a plugin."""

    name: str
    enabled: bool = True
    settings: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.settings is None:
            self.settings = {}


class PluginConfigManager:
    """Manages plugin configurations."""

    def __init__(self, config_file: Path):
        """Initialize plugin config manager.

        Args:
            config_file: Path to the YAML config file
        """
        self.config_file = Path(config_file)
        self._configs: Dict[str, PluginConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load configurations from file."""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f) or {}

            for name, config in data.items():
                self._configs[name] = PluginConfig(
                    name=name,
                    enabled=config.get("enabled", True),
                    settings=config.get("settings", {}),
                )
        except (yaml.YAMLError, AttributeError):
            # Invalid YAML or unexpected format, use empty configs
            pass

    def _save_configs(self) -> None:
        """Save configurations to file."""
        data = {
            name: {"enabled": config.enabled, "settings": config.settings}
            for name, config in self._configs.items()
        }

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            yaml.safe_dump(data, f)

    def get_config(self, plugin_name: str) -> PluginConfig:
        """Get configuration for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin configuration, creating new one if it doesn't exist
        """
        if plugin_name not in self._configs:
            self._configs[plugin_name] = PluginConfig(name=plugin_name)
            self._save_configs()
        return self._configs[plugin_name]

    def update_config(self, plugin_name: str, settings: Dict[str, Any]) -> None:
        """Update plugin configuration settings.

        Args:
            plugin_name: Name of the plugin
            settings: New settings to apply
        """
        config = self.get_config(plugin_name)
        config.settings.update(settings)
        self._save_configs()

    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a plugin.

        Args:
            plugin_name: Name of the plugin to enable
        """
        config = self.get_config(plugin_name)
        config.enabled = True
        self._save_configs()

    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin.

        Args:
            plugin_name: Name of the plugin to disable
        """
        config = self.get_config(plugin_name)
        config.enabled = False
        self._save_configs()

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled.

        Args:
            plugin_name: Name of the plugin to check

        Returns:
            True if the plugin is enabled, False otherwise
        """
        return self.get_config(plugin_name).enabled

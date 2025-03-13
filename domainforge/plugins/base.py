"""Base plugin class for the plugin system."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PluginConfig:
    """Configuration for a plugin."""

    enabled: bool = True
    settings: Dict[str, Any] = dict()


class BasePlugin:
    """Base class for all plugins."""

    def __init__(self, config: Optional[PluginConfig] = None):
        """Initialize the plugin.

        Args:
            config: Plugin configuration.
        """
        self.config = config or PluginConfig()

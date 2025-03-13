"""Plugin registry for DomainForge."""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from .config import PluginConfigManager


class PluginRegistry:
    """Registry for managing plugin sources and metadata."""

    def __init__(
        self,
        registry_url: str,
        cache_dir: Optional[Path] = None,
        config_manager: Optional[PluginConfigManager] = None,
    ):
        """Initialize plugin registry.

        Args:
            registry_url: URL of the plugin registry
            cache_dir: Directory for caching registry data
            config_manager: Plugin configuration manager
        """
        self.registry_url = registry_url
        self.cache_dir = cache_dir or Path.home() / ".domainforge" / "registry"
        self.config_manager = config_manager
        self._plugins: Dict[str, dict] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached plugin data."""
        if not self.cache_dir.exists():
            return

        try:
            cache_file = self.cache_dir / "plugins.json"
            if cache_file.exists():
                with open(cache_file) as f:
                    self._plugins = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._plugins = {}

    def _save_cache(self) -> None:
        """Save plugin data to cache."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "plugins.json"

        with open(cache_file, "w") as f:
            json.dump(self._plugins, f)

    def refresh(self) -> None:
        """Refresh plugin registry from remote source."""
        try:
            response = requests.get(self.registry_url)
            response.raise_for_status()
            self._plugins = response.json()
            self._save_cache()
        except (requests.RequestException, json.JSONDecodeError):
            # If refresh fails, keep using cached data
            pass

    def get_plugin(self, name: str) -> Optional[dict]:
        """Get plugin metadata by name.

        Args:
            name: Name of the plugin

        Returns:
            Plugin metadata or None if not found
        """
        return self._plugins.get(name)

    def list_plugins(self) -> List[dict]:
        """List all available plugins.

        Returns:
            List of plugin metadata
        """
        return list(self._plugins.values())

    def search_plugins(self, query: str) -> List[dict]:
        """Search plugins by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching plugin metadata
        """
        query = query.lower()
        return [
            plugin
            for plugin in self._plugins.values()
            if query in plugin["name"].lower()
            or query in plugin.get("description", "").lower()
        ]


"""
Dummy PluginRegistry implementation for testing purposes.
This allows tests to patch the registry without error.
"""


class DummyPluginRegistry:
    """A mock plugin registry implementation used for testing purposes.

    This class provides a simplified version of the PluginRegistry interface
    that can be used in test environments without making actual network calls.
    """
    def __init__(self, registry_url: str):
        self.registry_url = registry_url

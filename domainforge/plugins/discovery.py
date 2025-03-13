"""Plugin discovery and loading utilities."""

import logging
import sys
from pathlib import Path
from typing import List

from .plugin_manager import PluginManager
from .template_plugin import TemplatePlugin
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


def find_plugins() -> List[TemplatePlugin]:
    """Find and load all installed plugins."""
    settings = get_settings()
    plugin_manager = PluginManager(settings.plugins_dir)

    plugins: List[TemplatePlugin] = []
    for name in plugin_manager.list_plugins():
        plugin = plugin_manager.get_plugin(name)
        if plugin:
            plugins.append(plugin)

    return plugins


def ensure_plugin_paths() -> None:
    """Ensure plugin directories are in Python path."""
    settings = get_settings()
    plugins_dir = settings.plugins_dir

    if not plugins_dir.exists():
        return

    # Add plugins directory to Python path if not already there
    plugins_dir_str = str(plugins_dir.resolve())
    if plugins_dir_str not in sys.path:
        sys.path.insert(0, plugins_dir_str)

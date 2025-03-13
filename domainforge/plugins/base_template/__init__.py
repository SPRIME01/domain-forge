"""Base template plugin for DomainForge.

This plugin provides the default templates for code generation.
"""

from pathlib import Path
from typing import Any, Dict

from ..plugin import Plugin, PluginMetadata, PluginType


class BaseTemplatePlugin(Plugin):
    """Base template plugin providing default code generation templates."""

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="base-template",
            version="0.1.0",
            description="Default code generation templates",
            author="DomainForge Team",
            plugin_type=PluginType.TEMPLATE,
        )

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin.

        Args:
        ----
            config: Plugin configuration.
        """
        pass

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def get_template_path(self) -> Path:
        """Get the path to template files.

        Returns:
        -------
            Path to template directory.
        """
        return Path(__file__).parent / "templates"

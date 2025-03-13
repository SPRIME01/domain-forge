"""Mock plugin for testing the plugin system."""

from typing import Dict, Any

from domainforge.plugins.base_plugin import BasePlugin
from domainforge.plugins.template_plugin import PluginMetadata


class MockPlugin(BasePlugin):
    """A mock plugin for testing purposes.

    This plugin implements the minimal required functionality
    to test the plugin system.
    """

    def __init__(self):
        """Initialize the mock plugin."""
        super().__init__()
        self.metadata = PluginMetadata(
            name="mock-plugin",
            version="1.0.0",
            description="Mock plugin for testing",
            author="DomainForge Testing Team",
            plugin_type="test",
        )
        self.initialized = False
        self.config: Dict[str, Any] = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration.

        Args:
            config: Configuration dictionary
        """
        self.initialized = True
        self.config = config

    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        self.initialized = False

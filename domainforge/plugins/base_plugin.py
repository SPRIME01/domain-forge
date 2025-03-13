"""Base plugin interface for DomainForge plugins.

This module defines the base classes and interfaces required for implementing
plugins in the DomainForge system. All plugins must extend the BasePlugin class
and implement its required methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PluginMetadata:
    """Metadata for a plugin.

    This class holds metadata about a plugin including its name, version,
    description, author, and type. It is used for plugin discovery, registration,
    and management.
    """

    name: str
    version: str
    description: str
    author: str
    plugin_type: str


class BasePlugin(ABC):
    """Base class for all DomainForge plugins.

    This abstract base class defines the interface that all plugins must implement.
    It provides common functionality and structure that ensures plugins can be
    properly discovered, initialized, and managed within the DomainForge system.
    """

    def __init__(self) -> None:
        """Initialize the plugin.

        Sets up the plugin with default values. Subclasses should call this
        using super().__init__() and then set their specific metadata.
        """
        self.metadata: Optional[PluginMetadata] = None

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration.

        This method is called by the plugin manager when the plugin is first loaded.
        It should set up any resources required by the plugin.

        Args:
            config: A dictionary containing configuration values for the plugin
        """
        pass

    def cleanup(self) -> None:
        """Clean up resources used by the plugin.

        This method is called when the plugin is being uninstalled or the
        application is shutting down. It should release any resources allocated
        during the plugin's lifecycle.
        """
        pass

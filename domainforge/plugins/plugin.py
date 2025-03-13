"""Plugin system interfaces and base classes.

This module provides the core interfaces and base classes for DomainForge's plugin system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PluginType(Enum):
    """Types of plugins supported by DomainForge."""

    GENERATOR = "generator"  # Code generation plugins
    TRANSFORMER = "transformer"  # DSL transformation plugins
    TEMPLATE = "template"  # Template plugins
    VALIDATOR = "validator"  # DSL validation plugins


@dataclass
class PluginMetadata:
    """Metadata for a DomainForge plugin."""

    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    license: str = "MIT"

    def __post_init__(self):
        """Initialize optional fields."""
        if self.dependencies is None:
            self.dependencies = []


class Plugin(ABC):
    """Base class for all DomainForge plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration.

        Args:
        ----
            config: Plugin-specific configuration dictionary.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass


class PluginError(Exception):
    """Base class for plugin-related exceptions."""

    pass


class PluginNotFoundError(PluginError):
    """Exception raised when a plugin cannot be found."""

    pass


class PluginLoadError(PluginError):
    """Exception raised when a plugin fails to load."""

    pass


class PluginValidationError(PluginError):
    """Exception raised when a plugin fails validation."""

    pass

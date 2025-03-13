"""Package for DomainForge plugins.

This package contains base plugin classes and implementations for various
plugin types including template plugins, code generation plugins, etc.
"""

from .base_plugin import BasePlugin, PluginMetadata
from .plugin_manager import PluginManager
from .template_plugin import TemplatePlugin

# For backward compatibility, rename to Plugin
Plugin = BasePlugin


# Define plugin types as constants
class PluginType:
    """Constants for plugin types."""

    TEMPLATE = "template"
    GENERATOR = "generator"
    MODEL = "model"
    EXPORT = "export"
    IMPORT = "import"
    UTIL = "util"
    TEST = "test"


__all__ = [
    "BasePlugin",
    "Plugin",  # Add the aliased name
    "PluginMetadata",
    "PluginManager",
    "TemplatePlugin",
    "PluginType",  # Add the PluginType class
]

"""Plugin manager for loading and managing DomainForge plugins."""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, cast

from domainforge.plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

# Type variable for plugin classes
P = TypeVar("P", bound=BasePlugin)


class PluginManager:
    """Manages plugin discovery, registration and lifecycle.

    This class is responsible for finding, loading, and managing plugins
    throughout the application's lifecycle. It maintains a registry of loaded
    plugins and provides methods to access them by type or name.
    """

    def __init__(self):
        """Initialize the plugin manager with an empty registry."""
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_paths: List[Path] = []

    def discover_plugins(self, plugin_paths: Optional[List[Path]] = None) -> None:
        """Discover plugins from specified paths.

        Args:
            plugin_paths: Optional paths to search for plugins. If None,
                          default paths will be used.
        """
        if plugin_paths:
            self.plugin_paths.extend(plugin_paths)

        # Add default plugin paths if none provided
        if not self.plugin_paths:
            # Add built-in plugins
            import domainforge.plugins as builtin_plugins

            builtin_path = Path(builtin_plugins.__file__).parent
            self.plugin_paths.append(builtin_path)

            # TODO: Add user plugin paths if needed

        self._load_plugins_from_paths()

    def _load_plugins_from_paths(self) -> None:
        """Load plugins from the configured paths."""
        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                logger.warning(f"Plugin path {plugin_path} does not exist, skipping")
                continue

            logger.info(f"Searching for plugins in {plugin_path}")

            # Convert Path to module path
            if str(plugin_path).endswith("__pycache__"):
                continue

            try:
                # Handle both package and file-based plugins
                if plugin_path.is_dir():
                    self._load_package_plugins(plugin_path)
                else:
                    self._load_file_plugin(plugin_path)
            except Exception as e:
                logger.error(f"Error loading plugins from {plugin_path}: {e}")

    def _load_package_plugins(self, package_path: Path) -> None:
        """Load plugins from a package directory.

        Args:
            package_path: Path to the package directory
        """
        package_name = package_path.name

        # Check if it's a proper Python package
        if not (package_path / "__init__.py").exists():
            logger.debug(f"{package_path} is not a Python package, skipping")
            return

        # Try to import the package
        try:
            package = importlib.import_module(f"domainforge.plugins.{package_name}")

            # Look for plugin classes in the package
            for _, name, is_pkg in pkgutil.iter_modules([str(package_path)]):
                if is_pkg:
                    # Recursively check subpackages
                    self._load_package_plugins(package_path / name)
                else:
                    # Load module and check for plugin classes
                    module_name = f"domainforge.plugins.{package_name}.{name}"
                    self._load_plugin_from_module(module_name)

        except ImportError as e:
            logger.error(f"Failed to import package {package_name}: {e}")

    def _load_file_plugin(self, file_path: Path) -> None:
        """Load a plugin from a single Python file.

        Args:
            file_path: Path to the Python file
        """
        if not file_path.name.endswith(".py"):
            return

        if file_path.name == "__init__.py":
            return

        # Determine module name from file path
        try:
            # Convert file path to module path
            module_path = file_path.relative_to(Path(__file__).parent.parent)
            module_name = ".".join(
                ["domainforge"] + list(module_path.parts[:-1]) + [module_path.stem]
            )
            self._load_plugin_from_module(module_name)
        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")

    def _load_plugin_from_module(self, module_name: str) -> None:
        """Load plugins from a module by name.

        Args:
            module_name: Fully qualified module name
        """
        try:
            module = importlib.import_module(module_name)

            # Find all plugin classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if this is a plugin class (but not the base class)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    # Create instance and register it
                    try:
                        plugin_instance = attr()
                        metadata = plugin_instance.metadata

                        if metadata and metadata.name:
                            self.register_plugin(plugin_instance)
                            logger.info(
                                f"Loaded plugin: {metadata.name} ({metadata.version})"
                            )
                        else:
                            logger.warning(
                                f"Plugin class {attr_name} has no metadata, skipping"
                            )
                    except Exception as e:
                        logger.error(f"Error instantiating plugin {attr_name}: {e}")

        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading plugins from {module_name}: {e}")

    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a plugin in the manager.

        Args:
            plugin: Plugin instance to register
        """
        if not plugin.metadata:
            raise ValueError("Plugin has no metadata")

        name = plugin.metadata.name

        if name in self.plugins:
            logger.warning(f"Plugin {name} already registered, overwriting")

        self.plugins[name] = plugin

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name to retrieve

        Returns:
            Plugin instance if found, None otherwise
        """
        return self.plugins.get(name)

    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, BasePlugin]:
        """Get all plugins of a specific type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            Dictionary of plugin instances by name
        """
        return {
            name: plugin
            for name, plugin in self.plugins.items()
            if plugin.metadata and plugin.metadata.plugin_type == plugin_type
        }

    def get_plugins(self) -> Dict[str, BasePlugin]:
        """Get all registered plugins.

        Returns:
            Dictionary of all plugin instances by name
        """
        return self.plugins.copy()

    def uninstall(self, plugin_name: str) -> bool:
        """Uninstall a plugin by name.

        Args:
            plugin_name: Name of the plugin to uninstall

        Returns:
            True if plugin was found and uninstalled, False otherwise
        """
        if plugin_name in self.plugins:
            # Call cleanup method if available
            plugin = self.plugins[plugin_name]
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error during plugin cleanup for {plugin_name}: {e}")

            # Remove from registry
            del self.plugins[plugin_name]
            logger.info(f"Plugin {plugin_name} uninstalled")
            return True

        logger.warning(f"Plugin {plugin_name} not found, cannot uninstall")
        return False

    def get_plugin_of_type(
        self, plugin_type: str, plugin_class: Type[P]
    ) -> Dict[str, P]:
        """Get plugins of a specific type and class.

        This is a type-safe way to get plugins of a specific derived type.

        Args:
            plugin_type: The type of plugin to filter by
            plugin_class: The class type to cast the plugins to

        Returns:
            Dictionary of plugin instances by name, cast to the specified type
        """
        plugins = self.get_plugins_by_type(plugin_type)
        return {
            name: cast(plugin_class, plugin)
            for name, plugin in plugins.items()
            if isinstance(plugin, plugin_class)
        }

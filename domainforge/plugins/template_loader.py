"""Template loader for DomainForge plugins."""

from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import (
    Environment,
    FileSystemLoader,
    Template,
    TemplateNotFound,
    select_autoescape,
)
from .plugin_manager import PluginManager


class TemplateLoader:
    """Loads templates from core templates and plugins."""

    def __init__(self, plugin_manager: PluginManager, core_templates_dir: Path):
        """Initialize template loader.

        Args:
            plugin_manager: Plugin manager instance
            core_templates_dir: Path to core templates directory
        """
        self.plugin_manager = plugin_manager
        self.core_templates_dir = Path(core_templates_dir)
        self._env = None
        self._initialize_environment()

    def _initialize_environment(self) -> None:
        """Initialize Jinja2 environment with all template directories."""
        template_dirs = self.get_template_dirs()

        self._env = Environment(
            loader=FileSystemLoader([str(path) for path in template_dirs.values()]),
            autoescape=select_autoescape(["html", "xml", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template_dirs(self) -> Dict[str, Path]:
        """Get all template directories.

        Returns:
            Dictionary mapping template sources to their filesystem paths
        """
        dirs = {}

        # Add core templates
        if self.core_templates_dir.exists():
            dirs["core"] = self.core_templates_dir

        # Add plugin templates
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            if hasattr(plugin, "get_template_paths"):
                template_paths = plugin.get_template_paths()
                for category, path in template_paths.items():
                    if path.exists():
                        dirs[f"{plugin_name}_{category}"] = path

        return dirs

    def get_template(
        self, template_name: str, framework: Optional[str] = None
    ) -> Template:
        """Get a template by name and optional framework.

        Args:
            template_name: Name of the template to load
            framework: Optional framework to look for specific template

        Returns:
            Loaded template

        Raises:
            TemplateNotFound: If template cannot be found
        """
        if framework:
            try:
                return self._env.get_template(f"{framework}/{template_name}")
            except TemplateNotFound:
                pass  # Fall back to base template

        return self._env.get_template(template_name)

    def list_templates(self, framework: Optional[str] = None) -> List[str]:
        """List available templates, optionally filtered by framework.

        Args:
            framework: Optional framework to filter templates

        Returns:
            List of template names
        """
        all_templates = self._env.list_templates()

        if framework:
            return [t for t in all_templates if t.startswith(f"{framework}/")]

        return all_templates

"""Template plugin implementation for code generation.

This module defines the TemplatePlugin class, which is a specialized plugin
type for handling code templates in the DomainForge system.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from domainforge.plugins.base_plugin import BasePlugin, PluginMetadata


class TemplatePlugin(BasePlugin):
    """Base class for template plugins.

    Template plugins provide templates for code generation in different
    programming languages and frameworks. They are used by code generators
    to produce output files from domain models.
    """

    def __init__(self) -> None:
        """Initialize a new template plugin instance."""
        super().__init__()
        self.template_dir: Path = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the template plugin with configuration.

        Args:
            config: Configuration dictionary that may contain:
                - template_dir: Custom template directory path
        """
        template_dir_path = config.get("template_dir")
        if template_dir_path:
            base_dir = Path(template_dir_path)
        else:
            # Default to a directory relative to the plugin
            base_dir = self._get_default_template_dir()

        # Ensure template directory exists
        self.template_dir = base_dir / "templates"
        self.template_dir.mkdir(exist_ok=True, parents=True)

    def _get_default_template_dir(self) -> Path:
        """Get the default template directory.

        Returns:
            Path to the default template directory
        """
        # By default, use a directory in the user's home directory
        return Path(os.path.expanduser("~")) / ".domainforge"

    def get_template_paths(self) -> Dict[str, Path]:
        """Get paths to available templates.

        Returns:
            Dictionary mapping template categories to their paths
        """
        if not self.template_dir:
            raise ValueError("Template directory not initialized")

        paths = {}
        backend_dir = self.template_dir / "backend"
        frontend_dir = self.template_dir / "frontend"

        if backend_dir.exists():
            paths["backend"] = backend_dir

        if frontend_dir.exists():
            paths["frontend"] = frontend_dir

        return paths

    def get_supported_frameworks(self) -> Dict[str, List[str]]:
        """Get list of supported frameworks.

        Returns:
            Dictionary mapping template categories to lists of supported frameworks
        """
        frameworks = {"backend": ["fastapi", "django"], "frontend": ["react", "vue"]}
        return frameworks

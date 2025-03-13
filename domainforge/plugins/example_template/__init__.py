"""Example template plugin for DomainForge."""

from pathlib import Path
from typing import Dict, List
from domainforge.plugins import TemplatePlugin, PluginMetadata, PluginType


class ExampleTemplatePlugin(TemplatePlugin):
    """Example template plugin providing FastAPI and React templates."""

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="example-template",
            version="0.1.0",
            description="Example code generation templates",
            author="DomainForge Team",
            plugin_type=PluginType.TEMPLATE,
        )

    def initialize(self, config: dict) -> None:
        """Initialize the plugin.

        Args:
            config: Plugin configuration dictionary
        """
        self.template_dir = Path(__file__).parent / "templates"
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)

        # Create backend templates directory
        backend_dir = self.template_dir / "backend" / "fastapi"
        backend_dir.mkdir(parents=True, exist_ok=True)

        # Create frontend templates directory
        frontend_dir = self.template_dir / "frontend" / "react"
        frontend_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def get_template_paths(self) -> Dict[str, Path]:
        """Get paths to template directories.

        Returns:
            Dictionary mapping template categories to filesystem paths
        """
        return {
            "backend": self.template_dir / "backend",
            "frontend": self.template_dir / "frontend",
        }

    def get_supported_frameworks(self) -> Dict[str, List[str]]:
        """Get supported frameworks for templates.

        Returns:
            Dictionary mapping categories to lists of supported frameworks
        """
        return {"backend": ["fastapi", "django"], "frontend": ["react", "vue"]}

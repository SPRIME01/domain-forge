"""Code generator module for converting domain models to code.

This module contains the CodeGenerator class that works with TemplatePlugins
to generate code for different languages and frameworks.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template

from domainforge.plugins.plugin_manager import PluginManager
from domainforge.plugins.template_plugin import TemplatePlugin


class CodeGenerator:
    """Generates code from domain models using templates from plugins.

    This class is responsible for taking domain models and generating
    corresponding code files using templates provided by template plugins.
    It supports multiple programming languages and frameworks.
    """

    def __init__(self, plugin_manager: Optional[PluginManager] = None):
        """Initialize the code generator.

        Args:
            plugin_manager: Optional plugin manager instance. If not provided,
                            a new instance will be created.
        """
        self.plugin_manager = plugin_manager or PluginManager()
        self.jinja_env = Environment(
            loader=FileSystemLoader("/"),  # Will be configured per template
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def generate(
        self,
        entity: Any,
        output_dir: Path,
        category: str = "backend",
        framework: str = "fastapi",
        template_name: Optional[str] = None,
    ) -> List[Path]:
        """Generate code from an entity model.

        Args:
            entity: The entity model to generate code from
            output_dir: Directory where generated code will be saved
            category: Category of code to generate (backend, frontend)
            framework: Framework to use for code generation
            template_name: Optional specific template name to use

        Returns:
            List of paths to the generated files

        Raises:
            ValueError: If no suitable template is found or templates are invalid
        """
        # Get template plugins
        template_plugins = self.plugin_manager.get_plugins_by_type("template")
        if not template_plugins:
            raise ValueError("No template plugins available")

        # For now, just use the first template plugin
        template_plugin = list(template_plugins.values())[0]

        # Check if framework is supported
        frameworks = template_plugin.get_supported_frameworks()
        if category not in frameworks:
            raise ValueError(f"Category '{category}' not supported")

        if framework not in frameworks[category]:
            raise ValueError(
                f"Framework '{framework}' not supported in category '{category}'"
            )

        # Get template paths
        try:
            template_paths = template_plugin.get_template_paths()
        except Exception as e:
            raise ValueError(f"Error getting template paths: {str(e)}")

        if category not in template_paths:
            raise ValueError(f"No templates available for category '{category}'")

        category_dir = template_paths[category]
        framework_dir = category_dir / framework

        if not framework_dir.exists():
            raise ValueError(f"No templates available for framework '{framework}'")

        # Find templates to use
        if template_name:
            templates = [framework_dir / template_name]
            if not templates[0].exists():
                raise ValueError(f"Template '{template_name}' not found")
        else:
            # Use all templates in the framework directory
            templates = list(framework_dir.glob("*.j2"))

        if not templates:
            raise ValueError(f"No templates found for framework '{framework}'")

        # Create output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True, parents=True)

        # Generate code from each template
        generated_files = []
        for template_path in templates:
            # Configure Jinja environment for this template
            template_dir = template_path.parent
            template_filename = template_path.name

            # Create a new environment with the correct template directory
            env = Environment(
                loader=FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )

            # Load and render the template
            template = env.get_template(template_filename)
            rendered = template.render(entity=entity)

            # Determine output filename
            output_filename = template_filename.replace(".j2", "")

            if "{{ entity.name" in output_filename:
                # Replace any entity name placeholders in the filename
                output_filename = output_filename.replace(
                    "{{ entity.name }}", entity.name
                )

            output_file = output_dir / output_filename

            # Write rendered content to file
            with open(output_file, "w") as f:
                f.write(rendered)

            generated_files.append(output_file)

        return generated_files

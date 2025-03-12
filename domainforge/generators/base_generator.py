"""Base generator class for code generation.

This module provides the base generator class that implements common functionality
for code generation, including template rendering and file system operations.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader

from ..core.models import BoundedContext, DomainModel


class BaseGenerator(ABC):
    """Base class for code generators.

    This abstract class provides common functionality for code generation,
    including template loading, rendering, and file system operations.
    """

    def __init__(self, output_dir: str, template_dir: Optional[str | Path] = None):
        """Initialize the generator.

        Args:
        ----
            output_dir: Directory where the generated code will be written. Will be
                      created if it doesn't exist.
            template_dir: Directory containing Jinja2 template files. If not provided,
                        will search in standard template locations.

        """
        self.output_dir = Path(output_dir)

        # If no template directory specified, use the default templates
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"
        else:
            template_dir = Path(template_dir)

        # Build search paths for templates with correct priorities
        search_paths = [
            template_dir,  # Specific template directory (if provided)
            Path(__file__).parent.parent / "templates",  # Core templates
            Path.cwd() / "templates",  # Templates in current working directory
            Path(__file__).parent.parent.parent / "templates",  # Project root templates
        ]

        # Initialize Jinja environment with multiple search paths
        self.env = Environment(
            loader=FileSystemLoader(
                [str(path) for path in search_paths if path.exists()]
            ),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self._register_filters()

    def generate(self, model: DomainModel) -> None:
        """Generate code from a domain model.

        Args:
        ----
            model: The domain model to generate code from. Contains all bounded contexts
                  and their components that will be used to generate the application code.

        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate code for each bounded context
        for context in model.bounded_contexts:
            self.generate_context(context)

    @abstractmethod
    def generate_context(self, context: BoundedContext) -> None:
        """Generate code for a bounded context.

        Args:
        ----
            context: The bounded context to generate code for. Contains the entities,
                    value objects, and other domain components that will be used to
                    generate the implementation for this context.

        """
        pass

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Path,
        mkdir: bool = True,
    ) -> None:
        """Render a template and write it to a file.

        Args:
        ----
            template_name: Name of the Jinja2 template file to render. Should be
                         relative to one of the template search paths.
            context: Dictionary of variables to pass to the template during rendering.
                    These will be available in the template as {{ variable }}.
            output_path: Path where the rendered file should be written. Parent
                       directories will be created if mkdir is True.
            mkdir: Whether to automatically create parent directories for the output
                  file. Defaults to True.

        """
        # Get the template
        template = self.env.get_template(template_name)

        # Create parent directories if they don't exist
        if mkdir:
            os.makedirs(output_path.parent, exist_ok=True)

        # Render the template and write to file
        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(template.render(**context))

    def _register_filters(self) -> None:
        """Register custom Jinja filters."""
        self.env.filters["camelcase"] = self._to_camel_case
        self.env.filters["pascalcase"] = self._to_pascal_case
        self.env.filters["snakecase"] = self._to_snake_case
        self.env.filters["kebabcase"] = self._to_kebab_case

    @staticmethod
    def _to_camel_case(s: str) -> str:
        """Convert a string to camelCase."""
        s = BaseGenerator._to_pascal_case(s)
        return s[0].lower() + s[1:]

    @staticmethod
    def _to_pascal_case(s: str) -> str:
        """Convert a string to PascalCase."""
        # Split on common separators
        parts = s.replace("-", " ").replace("_", " ").split()
        return "".join(p.capitalize() for p in parts)

    @staticmethod
    def _to_snake_case(s: str) -> str:
        """Convert a string to snake_case."""
        # First convert camelCase or PascalCase
        s1 = "".join("_" + c.lower() if c.isupper() else c for c in s).lstrip("_")
        # Then handle any remaining separators
        return s1.replace("-", "_").replace(" ", "_").lower()

    @staticmethod
    def _to_kebab_case(s: str) -> str:
        """Convert a string to kebab-case."""
        return BaseGenerator._to_snake_case(s).replace("_", "-")

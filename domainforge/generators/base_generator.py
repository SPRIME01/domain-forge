"""
Base generator class for code generation.

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
    """
    Base class for code generators.

    This abstract class provides common functionality for code generation,
    including template loading, rendering, and file system operations.
    """

    def __init__(self, output_dir: str, template_dir: Optional[str] = None):
        """
        Initialize the generator.

        Args:
            output_dir: Directory where generated code will be written
            template_dir: Directory containing template files (optional)
        """
        self.output_dir = Path(output_dir)

        # If no template directory specified, use the default templates
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        # Initialize Jinja environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self._register_filters()

    def generate(self, model: DomainModel) -> None:
        """
        Generate code from a domain model.

        Args:
            model: The domain model to generate code from
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate code for each bounded context
        for context in model.bounded_contexts:
            self.generate_context(context)

    @abstractmethod
    def generate_context(self, context: BoundedContext) -> None:
        """
        Generate code for a bounded context.

        Args:
            context: The bounded context to generate code for
        """
        pass

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Path,
        mkdir: bool = True,
    ) -> None:
        """
        Render a template and write it to a file.

        Args:
            template_name: Name of the template file
            context: Template context (variables)
            output_path: Path where the rendered file should be written
            mkdir: Whether to create parent directories (default: True)
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

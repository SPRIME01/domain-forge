"""Parser for the DomainForge DSL.

This module provides functionality to parse DomainForge DSL files into
a syntax tree that can be transformed into domain models.
"""

import os
from pathlib import Path
from typing import Optional

from lark import Lark, Tree, Transformer
from .models import DomainModel
from .transformer import DomainForgeTransformer


class ParsingError(Exception):
    """Exception raised when a parsing error occurs."""

    pass


class DomainForgeParser:
    """Parser for the DomainForge DSL using the Lark parsing library."""

    def __init__(
        self,
        grammar_file: Optional[str] = None,
        transformer: Optional[Transformer] = None,
    ) -> None:
        """Initialize the parser with the grammar from the specified file or the default grammar.

        Args:
        ----
            grammar_file: Path to a custom grammar file that defines the DomainForge DSL syntax.
                        If not provided, uses the default grammar.lark file from the core package.
                        The grammar file should be in Lark grammar format.
            transformer: An optional Lark Transformer to process the parsed tree; if not provided,
                        an identity transformer is used.
        """
        if grammar_file is None:
            # Get the directory where this script is located
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            # Use the default grammar file
            grammar_file = str(current_dir / "grammar.lark")

        # Load the grammar
        with open(grammar_file) as f:
            grammar = f.read()

        # Initialize the Lark parser
        self.parser = Lark(grammar, start="start", parser="lalr")

        # Set the transformer; if none provided, use the identity transformer
        if transformer is None:
            from lark import Transformer

            class IdentityTransformer(Transformer):
                def transform(self, tree: Tree) -> Tree:
                    return tree

            transformer = IdentityTransformer()

        self.transformer = transformer

    def parse(self, text: str) -> Tree:
        """Parse the input text according to the DomainForge grammar.

        Args:
        ----
            text (str): The DomainForge DSL text to parse

        Returns:
        -------
            lark.Tree: The parsed syntax tree

        """
        return self.parser.parse(text)

    def parse_file(self, file_path: str) -> Tree:
        """Parse a DomainForge DSL file.

        Args:
        ----
            file_path (str): Path to the .domainforge file

        Returns:
        -------
            lark.Tree: The parsed syntax tree

        """
        with open(file_path) as f:
            text = f.read()
        return self.parse(text)

    def parse_ui_components(self, input_text):
        """Parse UI component definitions with enhanced features including navigation flows"""
        try:
            tree = self.parser.parse(input_text)
            transformed = self.transformer.transform(tree)

            # The transformed result is now a dictionary, so we need to process components directly
            if "ui_components" in transformed:
                for component in transformed["ui_components"]:
                    if hasattr(component, "navigation_flow"):
                        self._process_navigation_flow(component)
                    if hasattr(component, "children"):
                        self._process_nested_components(component)

            return transformed
        except Exception as e:
            raise ParsingError(f"Error parsing UI components: {str(e)}") from e

    def _process_navigation_flow(self, component):
        """Process navigation flow rules for a component"""
        if not hasattr(component, "navigation_flow") or not component.navigation_flow:
            return

        # Convert navigation rules to appropriate model objects
        nav_rules = []
        for rule in component.navigation_flow:
            nav_rules.append(
                {
                    "event": rule.get("event"),
                    "target": rule.get("target"),
                    "params": rule.get("params", {}),
                }
            )

        component.navigation_rules = nav_rules

    def _process_nested_components(self, component):
        """Process navigation flows recursively in component trees."""
        # Process all children first (depth-first)
        for child in component.children:
            self._process_navigation_flow(child)
            if child.children:
                self._process_nested_components(child)

        # Add this line to also process the parent component
        self._process_navigation_flow(component)


def parse_domain_model(text: str) -> DomainModel:
    """Parse DomainForge DSL text into a domain model.

    Args:
        text: The DomainForge DSL text to parse

    Returns:
        DomainModel representing the parsed domain

    Raises:
        ParsingError: If there are syntax or semantic errors in the DSL text
    """
    transformer = DomainForgeTransformer()
    parser = DomainForgeParser(transformer=transformer)

    try:
        tree = parser.parse(text)
        return transformer.transform(tree)
    except Exception as e:
        raise ParsingError(f"Error parsing domain model: {str(e)}") from e

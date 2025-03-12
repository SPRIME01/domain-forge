"""Parser for the DomainForge DSL.

This module provides functionality to parse DomainForge DSL files into
a syntax tree that can be transformed into domain models.
"""

import os
from pathlib import Path

from lark import Lark, Tree


class DomainForgeParser:
    """Parser for the DomainForge DSL using the Lark parsing library."""

    def __init__(self, grammar_file: str | None = None) -> None:
        """Initialize the parser with the grammar from the specified file or the default grammar.

        Args:
        ----
            grammar_file: Path to a custom grammar file that defines the DomainForge DSL syntax.
                        If not provided, uses the default grammar.lark file from the core package.
                        The grammar file should be in Lark grammar format.

        """
        if grammar_file is None:
            # Get the directory where this script is located
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            # Use the default grammar file
            grammar_file = current_dir / "grammar.lark"

        # Load the grammar
        with open(grammar_file) as f:
            grammar = f.read()

        # Initialize the Lark parser
        self.parser = Lark(grammar, start="start", parser="lalr")

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

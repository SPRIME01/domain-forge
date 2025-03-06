"""
Parser for the DomainForge DSL.

This module provides functionality to parse DomainForge DSL files into
a syntax tree that can be transformed into domain models.
"""

import os
from pathlib import Path
from lark import Lark


class DomainForgeParser:
    """
    Parser for the DomainForge DSL using the Lark parsing library.
    """

    def __init__(self, grammar_file=None):
        """
        Initialize the parser with the grammar from the specified file or the default grammar.

        Args:
            grammar_file (str, optional): Path to the grammar file. If not provided,
                                         the default grammar file will be used.
        """
        if grammar_file is None:
            # Get the directory where this script is located
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            # Use the default grammar file
            grammar_file = current_dir / "grammar.lark"

        # Load the grammar
        with open(grammar_file, 'r') as f:
            grammar = f.read()

        # Initialize the Lark parser
        self.parser = Lark(grammar, start='start', parser='lalr')

    def parse(self, text):
        """
        Parse the input text according to the DomainForge grammar.

        Args:
            text (str): The DomainForge DSL text to parse

        Returns:
            lark.Tree: The parsed syntax tree
        """
        return self.parser.parse(text)

    def parse_file(self, file_path):
        """
        Parse a DomainForge DSL file.

        Args:
            file_path (str): Path to the .domainforge file

        Returns:
            lark.Tree: The parsed syntax tree
        """
        with open(file_path, 'r') as f:
            text = f.read()
        return self.parse(text)

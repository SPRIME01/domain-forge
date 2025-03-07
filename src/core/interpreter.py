"""
Interpreter for the DomainForge DSL.

This module coordinates the parsing and transformation of DSL files into
domain models that can be used by code generators.
"""

import json
from pathlib import Path
from typing import Dict, Union

from .parser import DomainForgeParser
from .transformer import DomainForgeTransformer
from .models import DomainModel


class DomainForgeInterpreter:
    """
    Main interpreter for the DomainForge DSL.

    This class coordinates the parsing and transformation of DSL files into
    domain models that can be used by code generators.
    """

    def __init__(self):
        """Initialize the interpreter with a parser and transformer."""
        self.parser = DomainForgeParser()
        self.transformer = DomainForgeTransformer()

    def interpret(self, text: str) -> DomainModel:
        """
        Interpret DomainForge DSL text and return a domain model.

        Args:
            text: The DSL text to interpret

        Returns:
            A DomainModel instance representing the interpreted model

        Raises:
            SyntaxError: If the DSL text contains syntax errors
            ValueError: If the model is semantically invalid
        """
        # Parse the text into a syntax tree
        tree = self.parser.parse(text)

        # Transform the tree into a domain model
        model = self.transformer.transform(tree)

        # Validate the model
        self._validate_model(model)

        return model

    def interpret_file(self, file_path: Union[str, Path]) -> DomainModel:
        """
        Interpret a DomainForge DSL file and return a domain model.

        Args:
            file_path: Path to the DSL file to interpret

        Returns:
            A DomainModel instance representing the interpreted model

        Raises:
            FileNotFoundError: If the file doesn't exist
            SyntaxError: If the DSL file contains syntax errors
            ValueError: If the model is semantically invalid
        """
        # Read and parse the file
        with open(file_path, 'r') as f:
            text = f.read()

        return self.interpret(text)

    def export_model(self, model: DomainModel, output_path: Union[str, Path]) -> None:
        """
        Export a domain model to JSON format.

        Args:
            model: The domain model to export
            output_path: Path where the JSON file should be written

        Raises:
            IOError: If the file cannot be written
        """
        # Convert model to dict using Pydantic's json() method
        model_json = model.model_dump_json(indent=2)

        # Write to file
        with open(output_path, 'w') as f:
            f.write(model_json)

    def _validate_model(self, model: DomainModel) -> None:
        """
        Validate a domain model for semantic correctness.

        Args:
            model: The domain model to validate

        Raises:
            ValueError: If the model is semantically invalid
        """
        errors = []

        # Track all defined names to catch duplicates
        defined_names: Dict[str, str] = {}

        # First pass: Register all names
        for context in model.bounded_contexts:
            # Check for duplicate context names
            if context.name in defined_names:
                errors.append(f"Duplicate bounded context name: {context.name}")
            defined_names[context.name] = "context"

            # Register entity names
            for entity in context.entities:
                if entity.name in defined_names:
                    errors.append(
                        f"Duplicate entity name in context {context.name}: {entity.name}"
                    )
                defined_names[entity.name] = "entity"

            # Register value objects
            for vo in context.value_objects:
                if vo.name in defined_names:
                    errors.append(
                        f"Duplicate value object name in context {context.name}: {vo.name}"
                    )
                defined_names[vo.name] = "value_object"

            # Register services
            for service in context.services:
                if service.name in defined_names:
                    errors.append(
                        f"Duplicate service name in context {context.name}: {service.name}"
                    )
                defined_names[service.name] = "service"

            # Register repositories
            for repo in context.repositories:
                if repo.name in defined_names:
                    errors.append(
                        f"Duplicate repository name in context {context.name}: {repo.name}"
                    )
                defined_names[repo.name] = "repository"

        # Second pass: Validate relationships and properties
        for context in model.bounded_contexts:
            for entity in context.entities:
                # Validate entity properties
                property_names = set()
                for prop in entity.properties:
                    if prop.name in property_names:
                        errors.append(
                            f"Duplicate property name in entity {entity.name}: {prop.name}"
                        )
                    property_names.add(prop.name)

                # Validate relationships after all entities are registered
                for rel in entity.relationships:
                    # Check that target entities exist
                    if rel.target_entity not in defined_names:
                        errors.append(
                            f"Unknown target entity in relationship: {rel.target_entity}"
                        )

        if errors:
            raise ValueError("Model validation failed:\n" + "\n".join(errors))

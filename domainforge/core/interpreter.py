"""
Interpreter for the DomainForge DSL.

This module coordinates the parsing and transformation of DSL files into
domain models that can be used by code generators.
"""

from pathlib import Path
from typing import Dict, Union, List, Set

from .models import DomainModel
from .parser import DomainForgeParser
from .transformer import DomainForgeTransformer


class DomainForgeInterpreter:
    """
    Main interpreter for the DomainForge DSL.

    This class coordinates the parsing and transformation of DSL files into
    domain models that can be used by code generators.
    """

    def __init__(self) -> None:
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
        with open(file_path) as f:
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
        with open(output_path, "w") as f:
            f.write(model_json)

    def _validate_model(self, model: DomainModel) -> None:
        """
        Validate a domain model for semantic correctness.

        Args:
            model: The domain model to validate

        Returns:
            A list of validation error messages

        Raises:
            ValueError: If the model is semantically invalid
        """
        errors: List[str] = []

        # Validate contexts
        self._validate_contexts(model, errors)

        # Validate entities
        self._validate_entities(model, errors)

        if errors:
            raise ValueError("Model validation failed:\n" + "\n".join(errors))

    def _validate_contexts(self, model: DomainModel, errors: List[str]) -> None:
        """
        Validate bounded contexts for semantic correctness.

        Args:
            model: The domain model to validate
            errors: A list to collect validation error messages
        """
        defined_names: Dict[str, str] = {}

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

    def _validate_entities(self, model: DomainModel, errors: List[str]) -> None:
        """
        Validate entities for semantic correctness.

        Args:
            model: The domain model to validate
            errors: A list to collect validation error messages
        """
        # Initialize defined_names dictionary for the scope
        defined_names: Dict[str, str] = {}

        # First pass: collect all entity names
        for context in model.bounded_contexts:
            for entity in context.entities:
                defined_names[entity.name] = "entity"

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

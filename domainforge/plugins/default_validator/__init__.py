"""Default validator plugin for DomainForge.

This plugin provides the default validation rules for domain models.
"""

from pathlib import Path
from typing import Any, Dict, List

from ..plugin import PluginMetadata, PluginType
from ..validator import ValidatorPlugin, ValidationResult
from ...core.parser import DomainForgeParser
from ...core.transformer import DomainForgeTransformer


class DefaultValidatorPlugin(ValidatorPlugin):
    """Default validator plugin implementing standard validation rules."""

    def __init__(self):
        """Initialize validator plugin."""
        self.parser = DomainForgeParser()
        self.transformer = DomainForgeTransformer()

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="default-validator",
            version="0.1.0",
            description="Default domain model validator",
            author="DomainForge Team",
            plugin_type=PluginType.VALIDATOR,
        )

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin.

        Args:
        ----
            config: Plugin configuration.
        """
        pass

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def validate_model(self, model: str, strict: bool = False) -> ValidationResult:
        """Validate a domain model.

        Args:
        ----
            model: Domain model DSL text to validate.
            strict: Whether to perform strict validation.

        Returns:
        -------
            ValidationResult containing validation status and any errors/warnings.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Basic syntax validation through parsing
        try:
            tree = self.parser.parse(model)
        except Exception as e:
            errors.append(f"Syntax error: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Transform and validate model
        try:
            domain_model = self.transformer.transform(tree)
        except Exception as e:
            errors.append(f"Transformation error: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Standard validation rules
        for context in domain_model.bounded_contexts:
            # Check context naming
            if not context.name[0].isupper():
                warnings.append(
                    f"Bounded context name '{context.name}' should be PascalCase"
                )

            for entity in context.entities:
                # Check entity naming
                if not entity.name[0].isupper():
                    if strict:
                        errors.append(
                            f"Entity name '{entity.name}' should be PascalCase"
                        )
                    else:
                        warnings.append(
                            f"Entity name '{entity.name}' should be PascalCase"
                        )

                # Check for required ID property
                has_id = False
                for prop in entity.properties:
                    if prop.name.lower() == "id":
                        has_id = True
                        break
                if not has_id:
                    if strict:
                        errors.append(
                            f"Entity '{entity.name}' should have an 'id' property"
                        )
                    else:
                        warnings.append(
                            f"Entity '{entity.name}' should have an 'id' property"
                        )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_file(self, file_path: str, strict: bool = False) -> ValidationResult:
        """Validate a domain model file.

        Args:
        ----
            file_path: Path to the domain model file.
            strict: Whether to perform strict validation.

        Returns:
        -------
            ValidationResult containing validation status and any errors/warnings.
        """
        try:
            with open(file_path) as f:
                model = f.read()
            return self.validate_model(model, strict)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to read file: {str(e)}"],
                warnings=[],
            )

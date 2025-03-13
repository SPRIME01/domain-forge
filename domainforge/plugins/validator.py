"""Validation plugin interface.

This module defines the interface for DomainForge validation plugins.
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from .plugin import Plugin


@dataclass
class ValidationResult:
    """Result of a validation check."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ValidatorPlugin(Plugin):
    """Base class for validator plugins."""

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

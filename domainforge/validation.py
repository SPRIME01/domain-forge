"""Validation module for DomainForge."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    messages: List[str]
    error: Optional[Exception] = None

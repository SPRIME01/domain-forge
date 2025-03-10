"""
Entity model.

This module defines the core Entity domain model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4


class Entity(BaseModel):
    """
    Core domain model representing an entity.

    This is a base model for domain entities following DDD principles.
    """

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()), description="Unique identifier"
    )
    name: str = Field(..., description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")

    class Config:
        """Pydantic model configuration."""

        frozen = True  # Immutable objects for better domain integrity

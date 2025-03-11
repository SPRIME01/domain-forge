"""Domain layer module."""

from .models.entity import Entity
from .repositories.entity_repository import EntityRepository

__all__ = ["Entity", "EntityRepository"]

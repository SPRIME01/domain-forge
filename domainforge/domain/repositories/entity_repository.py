"""Entity repository interface.

This module defines the repository protocol for entity persistence operations.
"""

from typing import List, Optional, Protocol

from ..models.entity import Entity


class EntityRepository(Protocol):
    """Protocol defining the interface for entity persistence operations."""

    async def get_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID.

        Args:
        ----
            entity_id: The unique identifier of the entity

        Returns:
        -------
            The entity if found, None otherwise

        """
        ...

    async def get_all(self) -> List[Entity]:
        """Get all entities.

        Returns
        -------
            A list of all entities

        """
        ...

    async def create(self, entity: Entity) -> Entity:
        """Create a new entity.

        Args:
        ----
            entity: The entity to create

        Returns:
        -------
            The created entity with its assigned ID

        """
        ...

    async def update(self, entity: Entity) -> Optional[Entity]:
        """Update an existing entity.

        Args:
        ----
            entity: The entity with updated values

        Returns:
        -------
            The updated entity if successful, None if entity not found

        """
        ...

    async def delete(self, entity_id: str) -> bool:
        """Delete an entity.

        Args:
        ----
            entity_id: The ID of the entity to delete

        Returns:
        -------
            True if the entity was deleted, False otherwise

        """
        ...

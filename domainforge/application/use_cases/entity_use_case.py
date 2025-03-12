"""Entity use case module.

This module provides the use cases for entity operations following clean architecture principles.
"""

from typing import List, Optional

from ...domain.models.entity import Entity
from ...domain.repositories.entity_repository import EntityRepository


class EntityUseCase:
    """Use case for entity operations.

    This class implements the business logic for entity-related operations
    by coordinating between the domain layer and infrastructure layer.
    """

    def __init__(self, repository: EntityRepository) -> None:
        """Initialize the use case with dependencies.

        Args:
        ----
            repository: The repository instance that provides entity persistence operations.
                      Used to interface with the data storage layer while maintaining
                      clean architecture boundaries.

        """
        self._repository = repository

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID.

        Args:
        ----
            entity_id: The unique identifier of the entity

        Returns:
        -------
            The entity if found, None otherwise

        """
        return await self._repository.get_by_id(entity_id)

    async def get_all_entities(self) -> List[Entity]:
        """Get all entities.

        Returns
        -------
            A list of all entities

        """
        return await self._repository.get_all()

    async def create_entity(self, entity: Entity) -> Entity:
        """Create a new entity.

        Args:
        ----
            entity: The entity to create

        Returns:
        -------
            The created entity with its assigned ID

        """
        return await self._repository.create(entity)

    async def update_entity(self, entity: Entity) -> Optional[Entity]:
        """Update an existing entity.

        Args:
        ----
            entity: The entity with updated values

        Returns:
        -------
            The updated entity if successful, None if entity not found

        """
        return await self._repository.update(entity)

    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity.

        Args:
        ----
            entity_id: The ID of the entity to delete

        Returns:
        -------
            True if the entity was deleted, False otherwise

        """
        return await self._repository.delete(entity_id)

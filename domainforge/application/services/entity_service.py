"""
Entity service module.

This module provides services for entity operations that may involve
additional business logic beyond the basic use cases.
"""

from typing import List, Optional, Dict, Any

from ...domain.models.entity import Entity
from ...domain.repositories.entity_repository import EntityRepository


class EntityService:
    """
    Service for entity-related operations.

    This service provides higher-level operations related to entities,
    potentially orchestrating multiple use cases or adding business logic.
    """

    def __init__(self, repository: EntityRepository) -> None:
        """
        Initialize the entity service.

        Args:
            repository: The repository for entity operations
        """
        self._repository = repository

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            The entity if found, None otherwise
        """
        return await self._repository.get_by_id(entity_id)

    async def list_entities(self) -> List[Entity]:
        """
        List all entities.

        Returns:
            A list of all entities
        """
        return await self._repository.get_all()

    async def create_entity(self, entity_data: Dict[str, Any]) -> str:
        """
        Create a new entity.

        Args:
            entity_data: Dictionary containing entity data

        Returns:
            The ID of the created entity
        """
        entity = Entity(**entity_data)
        created = await self._repository.create(entity)
        return created.id

    async def update_entity(
        self, entity_id: str, data: Dict[str, Any]
    ) -> Optional[Entity]:
        """
        Update an existing entity.

        Args:
            entity_id: The ID of the entity to update
            data: The updated entity data

        Returns:
            The updated entity if successful, None if entity not found
        """
        current = await self.get_entity(entity_id)
        if current is None:
            return None

        # Update fields
        updated_data = current.model_dump()
        updated_data.update(data)
        updated_entity = Entity(**updated_data)

        return await self._repository.update(updated_entity)

    async def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: The ID of the entity to delete

        Returns:
            True if entity was deleted, False if entity not found
        """
        return await self._repository.delete(entity_id)

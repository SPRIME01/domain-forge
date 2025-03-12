"""Tests for application services.

This module contains tests for the application service layer,
which orchestrates domain operations and transactions.
"""

import pytest
from typing import Any, Dict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Entity:
    id: str
    name: str
    description: str
    version: int
    created_at: datetime = field(default_factory=datetime.now)


class EntityService:
    """Sample service for testing."""

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    async def get_entity(self, entity_id: str) -> Any:
        """Get an entity by ID."""
        return await self.repository.get(entity_id)

    async def create_entity(self, entity_data: Dict[str, Any]) -> str:
        """Create a new entity."""
        entity = Entity(**entity_data)
        return await self.repository.add(entity)

    async def update_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Update an existing entity."""
        existing_entity = await self.repository.get(entity_id)
        if existing_entity is None:
            raise ValueError(f"Entity with ID {entity_id} not found")

        updated_entity = Entity(
            id=entity_id,
            name=entity_data.get("name", existing_entity.name),
            description=entity_data.get("description", existing_entity.description),
            version=existing_entity.version + 1,
        )

        await self.repository.update(updated_entity)

    async def delete_entity(self, entity_id: str) -> None:
        """Delete an entity by ID."""
        await self.repository.remove(entity_id)

    async def list_entities(self) -> list[Any]:
        """List all entities."""
        return await self.repository.list()


class TestEntityService:
    """Tests for the entity service."""

    @pytest.mark.asyncio
    async def test_create_entity(
        self, mock_repository: Any, sample_domain_entity_data: Dict[str, Any]
    ) -> None:
        """Test creating a new entity."""
        service = EntityService(mock_repository)

        entity_id = await service.create_entity(sample_domain_entity_data)

        assert entity_id == sample_domain_entity_data["id"]
        assert mock_repository.called_methods["add"] == 1

        # Verify entity was added to repository
        entity = await mock_repository.get(entity_id)
        assert entity.id == sample_domain_entity_data["id"]
        assert entity.name == sample_domain_entity_data["name"]

    @pytest.mark.asyncio
    async def test_get_entity(
        self, mock_repository: Any, sample_domain_entity_data: Dict[str, Any]
    ) -> None:
        """Test retrieving an entity by ID."""
        service = EntityService(mock_repository)
        await service.create_entity(sample_domain_entity_data)

        entity = await service.get_entity(sample_domain_entity_data["id"])

        assert entity is not None
        assert entity.id == sample_domain_entity_data["id"]
        assert mock_repository.called_methods["get"] == 1

    @pytest.mark.asyncio
    async def test_update_entity(
        self, mock_repository: Any, sample_domain_entity_data: Dict[str, Any]
    ) -> None:
        """Test updating an existing entity."""
        service = EntityService(mock_repository)
        await service.create_entity(sample_domain_entity_data)

        update_data = {"name": "Updated Name", "description": "Updated description"}
        await service.update_entity(sample_domain_entity_data["id"], update_data)

        updated_entity = await service.get_entity(sample_domain_entity_data["id"])

        assert updated_entity.name == "Updated Name"
        assert updated_entity.description == "Updated description"
        assert updated_entity.version == sample_domain_entity_data["version"] + 1
        assert mock_repository.called_methods["update"] == 1

    @pytest.mark.asyncio
    async def test_delete_entity(
        self, mock_repository: Any, sample_domain_entity_data: Dict[str, Any]
    ) -> None:
        """Test deleting an entity."""
        service = EntityService(mock_repository)
        await service.create_entity(sample_domain_entity_data)

        await service.delete_entity(sample_domain_entity_data["id"])

        entity = await service.get_entity(sample_domain_entity_data["id"])
        assert entity is None
        assert mock_repository.called_methods["remove"] == 1

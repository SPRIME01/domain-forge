"""
Integration tests combining repository, service, and domain behavior.
"""
import os
import tempfile
import pytest
import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

# Import the repository implementation from the infrastructure tests
from tests.infrastructure.test_repository import JsonFileRepository

# Define a simple domain entity
@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    def validate(self) -> bool:
        return bool(self.name)

    def to_dict(self) -> dict:
        data = asdict(self)
        data['created_at'] = data['created_at'].isoformat()
        return data


# Sample service that uses the repository and domain entity
class EntityService:
    def __init__(self, repository: JsonFileRepository) -> None:
        self.repository = repository

    async def create_entity(self, entity_data: dict) -> str:
        entity = Entity(**entity_data)
        if not entity.validate():
            raise ValueError("Invalid entity data")
        return await self.repository.add(entity.to_dict())

    async def get_entity(self, entity_id: str) -> dict:
        return await self.repository.get(entity_id)

    async def update_entity(self, entity_id: str, data: dict) -> None:
        current = await self.repository.get(entity_id)
        if current is None:
            raise ValueError(f"Entity {entity_id} not found")
        updated = current.copy()
        updated.update(data)
        updated["version"] = current["version"] + 1
        await self.repository.update(updated)

    async def delete_entity(self, entity_id: str) -> None:
        await self.repository.remove(entity_id)

    async def list_entities(self) -> list[dict]:
        return await self.repository.list()


@pytest.fixture
def repo_file() -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp:
        temp_path = temp.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
async def repository(repo_file: str) -> JsonFileRepository:
    return JsonFileRepository(repo_file)


@pytest.mark.asyncio
async def test_full_entity_flow(repository):
    repo_instance = await repository
    service = EntityService(repo_instance)
    # Create entity
    entity_data = {
        "id": "integration-1",
        "name": "Integration Test Entity",
        "description": "Full flow test",
        "version": 1
    }
    entity_id = await service.create_entity(entity_data)
    assert entity_id == "integration-1"

    # Get entity
    fetched = await service.get_entity(entity_id)
    assert fetched is not None
    assert fetched["name"] == "Integration Test Entity"

    # Update entity
    await service.update_entity(entity_id, {"name": "Updated Name"})
    updated = await service.get_entity(entity_id)
    assert updated["name"] == "Updated Name"
    assert updated["version"] == 2

    # List entities
    entities = await service.list_entities()
    assert len(entities) == 1

    # Delete entity
    await service.delete_entity(entity_id)
    deleted = await service.get_entity(entity_id)
    assert deleted is None

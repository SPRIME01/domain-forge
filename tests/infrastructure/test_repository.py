"""
Tests for infrastructure components.

This module contains tests for infrastructure components
like repositories, adapters, and external integrations.
"""
import pytest
import os
import json
import tempfile
from typing import Any, Dict, Generator, Optional
from pathlib import Path


class JsonFileRepository:
    """A sample file-based repository implementation for testing."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the repository file exists and is initialized."""
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID."""
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        return data.get(id)

    async def add(self, entity: Dict[str, Any]) -> str:
        """Add a new entity."""
        entity_id = entity["id"]
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        data[entity_id] = entity

        with open(self.file_path, 'w') as f:
            json.dump(data, f)

        return entity_id

    async def update(self, entity: Dict[str, Any]) -> None:
        """Update an existing entity."""
        entity_id = entity["id"]
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        if entity_id not in data:
            raise ValueError(f"Entity with ID {entity_id} not found")

        data[entity_id] = entity

        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    async def remove(self, id: str) -> None:
        """Remove an entity by ID."""
        with open(self.file_path, 'r') as f:
            data = json.load(f)

        if id in data:
            del data[id]

        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    async def list(self) -> list[Dict[str, Any]]:
        """List all entities."""
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        return list(data.values())


class TestJsonFileRepository:
    """Tests for the JsonFileRepository."""

    @pytest.fixture
    def repo_file(self) -> Generator[str, Any, None]:
        """Create a temporary file for the repository."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp:
            temp_path = temp.name
        yield temp_path
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def repository(self, repo_file: str) -> JsonFileRepository:
        """Create a repository instance."""
        return JsonFileRepository(repo_file)

    @pytest.mark.asyncio
    async def test_add_entity(self, repository: JsonFileRepository) -> None:
        """Test adding an entity to the repository."""
        entity = {"id": "1", "name": "Test Entity", "description": "Test description", "version": 1}
        entity_id = await repository.add(entity)
        assert entity_id == "1"

        # Verify entity was added
        saved_entity = await repository.get("1")
        assert saved_entity is not None
        assert saved_entity["name"] == "Test Entity"

    @pytest.mark.asyncio
    async def test_update_entity(self, repository: JsonFileRepository) -> None:
        """Test updating an entity in the repository."""
        entity = {"id": "1", "name": "Test Entity", "description": "Test description", "version": 1}
        await repository.add(entity)

        # Update the entity
        entity["name"] = "Updated Entity"
        entity["version"] = 2
        await repository.update(entity)

        # Verify entity was updated
        updated_entity = await repository.get("1")
        assert updated_entity is not None
        assert updated_entity["name"] == "Updated Entity"
        assert updated_entity["version"] == 2

    @pytest.mark.asyncio
    async def test_remove_entity(self, repository: JsonFileRepository) -> None:
        """Test removing an entity from the repository."""
        entity = {"id": "1", "name": "Test Entity", "description": "Test description", "version": 1}
        await repository.add(entity)

        # Remove the entity
        await repository.remove("1")

        # Verify entity was removed
        removed_entity = await repository.get("1")
        assert removed_entity is None

    @pytest.mark.asyncio
    async def test_list_entities(self, repository: JsonFileRepository) -> None:
        """Test listing all entities in the repository."""
        await repository.add({"id": "1", "name": "Entity 1", "version": 1})
        await repository.add({"id": "2", "name": "Entity 2", "version": 1})
        await repository.add({"id": "3", "name": "Entity 3", "version": 1})

        entities = await repository.list()

        assert len(entities) == 3
        assert any(entity["id"] == "1" for entity in entities)
        assert any(entity["id"] == "2" for entity in entities)
        assert any(entity["id"] == "3" for entity in entities)

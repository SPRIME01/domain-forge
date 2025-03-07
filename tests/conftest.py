"""
Configuration and fixtures for pytest.

This module contains shared fixtures and configuration for all test modules.
"""
import os
import sys
import pytest
from typing import Any, Dict, Generator, Optional
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def sample_domain_entity_data() -> Dict[str, Any]:
    """Fixture providing sample data for domain entity tests."""
    return {
        "id": "12345",
        "name": "Test Entity",
        "description": "A test entity for unit tests",
        "created_at": "2023-09-15T10:30:00Z",
        "version": 1
    }

@pytest.fixture
def mock_repository() -> Generator[Any, None, None]:
    """Fixture providing a mock repository for testing service layer."""
    # This would be replaced by an actual mock implementation
    class MockRepository:
        def __init__(self) -> None:
            self.items: Dict[str, Any] = {}
            self.called_methods: Dict[str, int] = {
                "get": 0, "add": 0, "update": 0, "remove": 0, "list": 0
            }

        async def get(self, id: str) -> Optional[Any]:
            self.called_methods["get"] += 1
            return self.items.get(id)

        async def add(self, entity: Any) -> str:
            self.called_methods["add"] += 1
            self.items[entity.id] = entity
            return entity.id

        async def update(self, entity: Any) -> None:
            self.called_methods["update"] += 1
            self.items[entity.id] = entity

        async def remove(self, id: str) -> None:
            self.called_methods["remove"] += 1
            if id in self.items:
                del self.items[id]

        async def list(self) -> list[Any]:
            self.called_methods["list"] += 1
            return list(self.items.values())

    mock_repo = MockRepository()
    yield mock_repo

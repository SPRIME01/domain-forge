"""API integration tests."""

from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domainforge.config.settings import get_settings

# Import directly from domainforge module
from domainforge.infrastructure.app import app
from domainforge.infrastructure.database import Base, get_session

# Create a test client
client = TestClient(app)

# Create a test database engine
settings = get_settings()
# Use in-memory SQLite database for testing
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

@pytest_asyncio.fixture(autouse=True)
async def setup_test_database() -> AsyncGenerator[None, None]:
    """Setup test database."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create a test session factory
    test_session_local = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Override the session dependency
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_local() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Set engine in app state to ensure it's available during tests
    app.state.engine = test_engine

    yield  # Run the tests

    # Clean up
    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_entity() -> None:
    """Test creating an entity via API."""
    response = client.post("/api/entities", json={"name": "Test Entity"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Entity"

    # Test for invalid input data
    invalid_response = client.post("/api/entities", json={"name": ""})
    assert invalid_response.status_code == 422

    # Test for boundary conditions
    boundary_response = client.post("/api/entities", json={"name": "a" * 100})
    assert boundary_response.status_code == 201
    assert boundary_response.json()["name"] == "a" * 100

@pytest.mark.asyncio
async def test_get_entity() -> None:
    """Test retrieving an entity via API."""
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then try to get it
    response = client.get(f"/api/entities/{entity_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Entity"

    # Test for performance under load
    for _ in range(1000):
        response = client.get(f"/api/entities/{entity_id}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_entity() -> None:
    """Test updating an entity via API."""
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then update it
    response = client.put(f"/api/entities/{entity_id}", json={"name": "Updated Entity"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Entity"

    # Test for concurrency issues
    import asyncio

    async def update_entity_concurrently():
        tasks = [
            client.put(f"/api/entities/{entity_id}", json={"name": f"Updated Entity {i}"})
            for i in range(10)
        ]
        await asyncio.gather(*tasks)

    await update_entity_concurrently()

@pytest.mark.asyncio
async def test_delete_entity() -> None:
    """Test deleting an entity via API."""
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/entities/{entity_id}")
    assert response.status_code == 204

    # Test for security vulnerabilities
    # Attempt to delete the same entity again
    security_response = client.delete(f"/api/entities/{entity_id}")
    assert security_response.status_code == 404

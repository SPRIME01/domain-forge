"""API integration tests."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Import directly from src module
from src.infrastructure.app import app
from src.infrastructure.database import get_session, Base
from src.api.models import Entity
from src.config.settings import get_settings

# Create a test client
client = TestClient(app)

# Create a test database engine
settings = get_settings()
# Use in-memory SQLite database for testing
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    """Setup test database."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create a test session factory
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    # Override the session dependency
    async def override_get_session():
        async with TestSessionLocal() as session:
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
async def test_create_entity():
    response = client.post("/api/entities", json={"name": "Test Entity"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Entity"

@pytest.mark.asyncio
async def test_get_entity():
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then try to get it
    response = client.get(f"/api/entities/{entity_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Entity"

@pytest.mark.asyncio
async def test_update_entity():
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then update it
    response = client.put(f"/api/entities/{entity_id}", json={"name": "Updated Entity"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Entity"

@pytest.mark.asyncio
async def test_delete_entity():
    # Create an entity first
    create_response = client.post("/api/entities", json={"name": "Test Entity"})
    entity_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/entities/{entity_id}")
    assert response.status_code == 204

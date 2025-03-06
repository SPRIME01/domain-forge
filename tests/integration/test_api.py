import pytest
from fastapi.testclient import TestClient
from src.infrastructure.app import app
from src.infrastructure.database import get_session, init_database, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings

# Create a test client
client = TestClient(app)

# Create a test database engine
settings = get_settings()
test_engine = create_async_engine(settings.DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# Dependency override for getting a test session
async def override_get_session():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # Initialize the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(init_database)
    yield
    # Drop the test database tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def test_create_entity():
    response = client.post("/api/entities", json={"name": "Test Entity"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Entity"

def test_get_entity():
    response = client.get("/api/entities/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Entity"

def test_update_entity():
    response = client.put("/api/entities/1", json={"name": "Updated Entity"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Entity"

def test_delete_entity():
    response = client.delete("/api/entities/1")
    assert response.status_code == 204

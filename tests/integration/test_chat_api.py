"""Integration tests for the chat API endpoints."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from domainforge.infrastructure.app import app
from domainforge.api.controllers.chat_controller import get_ai_client

client = TestClient(app)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    settings = MagicMock()
    settings.OPENAI_API_KEY = "test-api-key"
    settings.OPENAI_API_BASE = "https://api.openai.com/v1"
    settings.OPENAI_MODEL = "gpt-4"

    # Mock the get_settings function
    monkeypatch.setattr("domainforge.core.ai_client.get_settings", lambda: settings)
    return settings


@pytest.fixture
def mock_ai_client():
    """Mock AI client for testing."""
    mock = AsyncMock()

    # Configure standard generate_response behavior
    mock.generate_response.return_value = "Test response"

    # Configure special responses for specific test cases
    mock.extract_domain_model.return_value = {
        "contexts": [
            {
                "name": "TestContext",
                "entities": [{"name": "TestEntity", "properties": []}],
            }
        ]
    }

    # Override the dependency
    app.dependency_overrides[get_ai_client] = lambda: mock
    yield mock
    # Clean up
    app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    """Fixture to mock the OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_chat_send_endpoint(mock_create, mock_ai_client) -> None:
    """Test sending a message to the chat API endpoint."""
    # Configure mock response
    mock_ai_client.generate_response.return_value = "Test response"
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}

    response = client.post(
        "/api/chat/send", json={"content": "Tell me about domain-driven design"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) > 0
    assert data["messages"][0] == "Test response"


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Session continuity feature not implemented")
@patch("openai.ChatCompletion.create")
async def test_chat_with_session_continuity(mock_create) -> None:
    """Test chat session continuity with multiple messages."""
    # Create a new mock AI client specifically for this test
    mock_ai_client = AsyncMock()
    mock_ai_client.generate_response.side_effect = [
        "Let's model an e-commerce system",
        "Let's identify the entities",
    ]

    # Override the dependency for this test
    app.dependency_overrides[get_ai_client] = lambda: mock_ai_client

    try:
        # First message creates a session
        initial_response = client.post(
            "/api/chat/send",
            json={"content": "I want to model an e-commerce domain"},
        )

        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        session_id = initial_data["session_id"]
        assert initial_data["messages"][0] == "Let's model an e-commerce system"

        # Second message should maintain context
        follow_up_response = client.post(
            "/api/chat/send",
            json={
                "content": "What entities should we create?",
                "session_id": session_id,
            },
        )

        assert follow_up_response.status_code == 200
        follow_up_data = follow_up_response.json()
        assert follow_up_data["session_id"] == session_id
        assert follow_up_data["messages"][0] == "Let's identify the entities"

    finally:
        # Clean up the dependency override
        app.dependency_overrides = {}


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_api_key_management(mock_create, mock_ai_client) -> None:
    """Test setting and validating an API key."""
    # Configure mock for successful validation
    mock_ai_client.generate_response.return_value = "API key is valid"
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}

    # Test valid API key
    response = client.post(
        "/api/chat/api-key",
        json={
            "api_key": "sk-valid-api-key",
            "api_base": "https://custom-api.example.com",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "validated successfully" in data["message"].lower()


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_api_error_handling(mock_create, mock_ai_client) -> None:
    """Test handling of API errors."""
    # Configure mock to raise an exception
    mock_ai_client.generate_response.side_effect = Exception("API connection error")
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}

    # Test error handling
    response = client.post("/api/chat/send", json={"content": "This should fail"})

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "API connection error" in data["detail"]


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_chat_empty_message(mock_create) -> None:
    """Test handling of empty messages."""
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    response = client.post("/api/chat/send", json={"content": ""})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "empty message" in data["detail"].lower()


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_chat_invalid_request(mock_create) -> None:
    """Test handling of requests with invalid structure."""
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    # Missing required 'content' field
    response = client.post(
        "/api/chat/send", json={"invalid_field": "This should fail validation"}
    )
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create")
async def test_chat_malformed_json(mock_create) -> None:
    """Test handling of malformed JSON."""
    mock_create.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    response = client.post(
        "/api/chat/send", json={"content": "invalid json{content:test}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_nonexistent_session() -> None:
    """Test accessing a nonexistent chat session."""
    response = client.get("/api/chat/invalid-session-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_domain_model_extraction(mock_ai_client) -> None:
    """Test domain model extraction from messages."""
    # Configure mock for entity extraction
    mock_ai_client.extract_domain_model.return_value = {
        "contexts": [
            {
                "name": "TestContext",
                "entities": [{"name": "TestEntity", "properties": []}],
            }
        ]
    }

    mock_ai_client.generate_response.return_value = (
        "I understand you want to model a domain"
    )

    # Send a message that should trigger entity elicitation
    response = client.post(
        "/api/chat/send",
        json={"content": "I need to model a domain with users and orders"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) > 0

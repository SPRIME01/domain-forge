"""Integration tests for the chat API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from typing import Dict, Any

from domainforge.infrastructure.app import app
from domainforge.core.ai_client import AIClient

# Create a test client
client = TestClient(app)


@pytest.fixture
def mock_ai_client():
    """Mock the AI client for tests."""
    with patch(
        "domainforge.api.controllers.chat_controller.get_ai_client"
    ) as mock_get_client:
        mock_client = AsyncMock(spec=AIClient)

        # Default behavior for generate_response
        async def mock_generate_response(*args, **kwargs):
            return "This is a mock AI response"

        # Default behavior for extract_domain_model
        async def mock_extract_domain_model(description):
            return {
                "contexts": [
                    {
                        "name": "SampleContext",
                        "entities": [
                            {
                                "name": "SampleEntity",
                                "properties": [{"name": "id", "type": "UUID"}],
                            }
                        ],
                        "relationships": [],
                    }
                ]
            }

        mock_client.generate_response.side_effect = mock_generate_response
        mock_client.extract_domain_model.side_effect = mock_extract_domain_model
        mock_get_client.return_value = mock_client

        yield mock_client


@pytest.mark.asyncio
async def test_chat_send_endpoint(mock_ai_client) -> None:
    """Test sending a message to the chat API endpoint."""
    response = client.post(
        "/api/chat/send", json={"content": "Tell me about domain-driven design"}
    )

    # Check response status and structure
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) > 0
    assert "session_id" in data
    assert data["elicitation_stage"] == "introduction"  # Initial stage

    # Verify AI client was called correctly
    mock_ai_client.generate_response.assert_called_once()
    call_args = mock_ai_client.generate_response.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0]["role"] == "system"
    assert call_args[1]["role"] == "user"
    assert call_args[1]["content"] == "Tell me about domain-driven design"


@pytest.mark.asyncio
async def test_chat_with_session_continuity(mock_ai_client) -> None:
    """Test chat session continuity with multiple messages."""
    # First message creates a session
    initial_response = client.post(
        "/api/chat/send", json={"content": "I want to model an e-commerce domain"}
    )

    assert initial_response.status_code == 200
    session_id = initial_response.json()["session_id"]

    # Configure mock for second response
    async def mock_generate_response_2(*args, **kwargs):
        return "Let's discuss entities like Product and Customer"

    mock_ai_client.generate_response.side_effect = mock_generate_response_2

    # Second message should use the same session
    follow_up_response = client.post(
        "/api/chat/send",
        json={"content": "What entities should I have?", "session_id": session_id},
    )

    assert follow_up_response.status_code == 200
    assert follow_up_response.json()["session_id"] == session_id

    # Verify the message was sent in the session context
    call_args = mock_ai_client.generate_response.call_args[0][0]
    assert call_args[1]["content"] == "What entities should I have?"


@pytest.mark.asyncio
async def test_api_key_management(mock_ai_client) -> None:
    """Test setting and validating an API key."""

    # Configure mock for successful validation
    async def mock_generate_response(*args, **kwargs):
        return "API key is valid"

    mock_ai_client.generate_response.side_effect = mock_generate_response

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
    assert "validated successfully" in data["message"]

    # Configure mock for failed validation
    async def mock_generate_response_invalid(*args, **kwargs):
        return "Sorry, I don't see valid credentials"

    mock_ai_client.generate_response.side_effect = mock_generate_response_invalid

    # Test invalid API key
    response = client.post("/api/chat/api-key", json={"api_key": "sk-invalid-key"})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "validation failed" in data["message"]


@pytest.mark.asyncio
async def test_api_error_handling(mock_ai_client) -> None:
    """Test handling of API errors."""
    # Configure mock to raise an exception
    mock_ai_client.generate_response.side_effect = Exception("API connection error")

    # Test error handling
    response = client.post("/api/chat/send", json={"content": "This should fail"})

    assert response.status_code == 500
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_domain_model_extraction(mock_ai_client) -> None:
    """Test domain model extraction from messages."""

    # Configure mock for entity extraction
    async def stage_progress(*args, **kwargs):
        # This response will trigger progression to entity_elicitation stage
        return "Let's identify the key entities in your domain model."

    mock_ai_client.generate_response.side_effect = stage_progress

    # Send a message that should trigger entity elicitation
    response = client.post(
        "/api/chat/send",
        json={"content": "I need to model a domain with users and orders"},
    )

    assert response.status_code == 200

    # Wait for background tasks to complete (in real tests, we might need a better approach)
    import asyncio

    await asyncio.sleep(0.1)

    # Get session ID from response
    session_id = response.json()["session_id"]

    # Check the domain model for this session
    model_response = client.get(f"/api/chat/session/{session_id}")

    assert model_response.status_code == 200
    model_data = model_response.json()
    assert "entities" in model_data
    assert "relationships" in model_data


@pytest.mark.asyncio
async def test_chat_empty_message() -> None:
    """Test handling of empty messages."""
    response = client.post("/api/chat/send", json={"content": ""})

    # Empty messages should still be accepted but might generate generic responses
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data


@pytest.mark.asyncio
async def test_chat_invalid_request() -> None:
    """Test handling of requests with invalid structure."""
    # Missing required 'content' field
    response = client.post(
        "/api/chat/send", json={"invalid_field": "This should fail validation"}
    )

    # Should fail validation
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_chat_malformed_json() -> None:
    """Test handling of malformed JSON input."""
    response = client.post(
        "/api/chat/send",
        data="This is not valid JSON",
        headers={"Content-Type": "application/json"},
    )

    # Should return a bad request response
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_nonexistent_session() -> None:
    """Test requesting a non-existent session."""
    response = client.get("/api/chat/session/nonexistent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

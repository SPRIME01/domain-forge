"""Unit tests for the AI client integration."""

import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

import httpx
from pydantic import BaseModel

from domainforge.core.ai_client import AIClient, AIMessage, AIConversation, AIResponse


class TestAIClient:
    """Tests for the AIClient class."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Fixture providing mocked settings with API key."""
        with patch("domainforge.core.ai_client.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENAI_API_BASE = None
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_get_settings.return_value = mock_settings
            yield mock_settings

    @pytest.fixture
    def mock_httpx_client(self) -> AsyncMock:
        """Fixture providing a mocked httpx client."""
        with patch("domainforge.core.ai_client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_initialization_with_settings(
        self, mock_settings: MagicMock, mock_httpx_client: AsyncMock
    ) -> None:
        """Test client initialization using settings."""
        # Create client with settings
        client = AIClient()

        # Verify correct initialization
        assert client.api_key == "test-api-key"
        assert client.api_base == "https://api.openai.com/v1"  # Default value
        assert client.default_model == "gpt-4"

        # Verify httpx client was created with correct auth
        mock_httpx_client.assert_called_once()
        call_kwargs = mock_httpx_client.call_args.kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-api-key"

    def test_initialization_with_explicit_values(
        self, mock_settings: MagicMock, mock_httpx_client: AsyncMock
    ) -> None:
        """Test client initialization with explicit values."""
        # Create client with explicit values
        client = AIClient(
            api_key="explicit-api-key", api_base="https://custom-api.example.com/v1"
        )

        # Verify explicit values were used
        assert client.api_key == "explicit-api-key"
        assert client.api_base == "https://custom-api.example.com/v1"

        # Verify httpx client was created with correct auth
        call_kwargs = mock_httpx_client.call_args.kwargs
        assert call_kwargs["base_url"] == "https://custom-api.example.com/v1"
        assert call_kwargs["headers"]["Authorization"] == "Bearer explicit-api-key"

    def test_initialization_missing_api_key(self, mock_settings: MagicMock) -> None:
        """Test initialization fails when API key is missing."""
        # Remove API key from settings
        mock_settings.OPENAI_API_KEY = None

        # Also ensure environment variable is not set
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            # Attempting to create client should raise ValueError
            with pytest.raises(ValueError, match="API key not provided"):
                AIClient()

    @pytest.mark.asyncio
    async def test_generate_response_with_dict_messages(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """Test generating a response with a list of message dicts."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "resp-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-4",
            "choices": [
                {"message": {"role": "assistant", "content": "This is a test response"}}
            ],
            "usage": {"total_tokens": 10},
        }
        mock_httpx_client.post.return_value = mock_response

        # Create client and test messages
        client = AIClient()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]

        # Generate response
        response = await client.generate_response(messages)

        # Verify response
        assert response == "This is a test response"

        # Verify API call
        mock_httpx_client.post.assert_called_once_with(
            "/chat/completions",
            json={
                "model": "gpt-4",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
            },
        )

    @pytest.mark.asyncio
    async def test_generate_response_with_conversation_object(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """Test generating a response with an AIConversation object."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "resp-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-4",
            "choices": [
                {"message": {"role": "assistant", "content": "This is a test response"}}
            ],
            "usage": {"total_tokens": 10},
        }
        mock_httpx_client.post.return_value = mock_response

        # Create client and test conversation
        client = AIClient()
        conversation = AIConversation(
            messages=[
                AIMessage(role="system", content="You are a helpful assistant."),
                AIMessage(role="user", content="Hello!"),
            ],
            temperature=0.5,  # Custom temperature
            max_tokens=1000,  # Custom max_tokens
        )

        # Generate response
        response = await client.generate_response(conversation)

        # Verify response
        assert response == "This is a test response"

        # Verify API call with conversation-specific settings
        mock_httpx_client.post.assert_called_once()
        call_kwargs = mock_httpx_client.post.call_args.kwargs
        assert call_kwargs["json"]["temperature"] == 0.5
        assert call_kwargs["json"]["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_httpx_client: AsyncMock) -> None:
        """Test handling of API errors."""
        # Mock a failing API response
        mock_httpx_client.post.side_effect = httpx.HTTPError("API error")

        # Create client and test messages
        client = AIClient()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]

        # Generating response should propagate the error
        with pytest.raises(httpx.HTTPError, match="API error"):
            await client.generate_response(messages)

    @pytest.mark.asyncio
    async def test_extract_domain_model(self, mock_httpx_client: AsyncMock) -> None:
        """Test extracting a domain model from a description."""
        # Mock the API response with JSON content
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "resp-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-4",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": """
                        Based on your description, here's the domain model:
                        ```json
                        {
                            "contexts": [
                                {
                                    "name": "ECommerce",
                                    "entities": [
                                        {
                                            "name": "Product",
                                            "properties": [
                                                {"name": "id", "type": "UUID", "constraints": ["required"]},
                                                {"name": "name", "type": "String", "constraints": ["required"]}
                                            ]
                                        }
                                    ],
                                    "relationships": []
                                }
                            ]
                        }
                        ```
                        """,
                    }
                }
            ],
            "usage": {"total_tokens": 100},
        }
        mock_httpx_client.post.return_value = mock_response

        # Create client and test description
        client = AIClient()
        description = "I need an e-commerce system with products."

        # Extract domain model
        model = await client.extract_domain_model(description)

        # Verify model structure
        assert "contexts" in model
        assert len(model["contexts"]) == 1
        assert model["contexts"][0]["name"] == "ECommerce"
        assert len(model["contexts"][0]["entities"]) == 1
        assert model["contexts"][0]["entities"][0]["name"] == "Product"

    @pytest.mark.asyncio
    async def test_refine_domain_model(self, mock_httpx_client: AsyncMock) -> None:
        """Test refining an existing domain model based on feedback."""
        # Initial model
        current_model = {
            "contexts": [
                {
                    "name": "ECommerce",
                    "entities": [
                        {
                            "name": "Product",
                            "properties": [
                                {
                                    "name": "id",
                                    "type": "UUID",
                                    "constraints": ["required"],
                                },
                                {
                                    "name": "name",
                                    "type": "String",
                                    "constraints": ["required"],
                                },
                            ],
                        }
                    ],
                    "relationships": [],
                }
            ]
        }

        # Mock the API response with refined model
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "resp-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-4",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": """
                        I've refined the model based on your feedback:
                        ```json
                        {
                            "contexts": [
                                {
                                    "name": "ECommerce",
                                    "entities": [
                                        {
                                            "name": "Product",
                                            "properties": [
                                                {"name": "id", "type": "UUID", "constraints": ["required"]},
                                                {"name": "name", "type": "String", "constraints": ["required"]},
                                                {"name": "price", "type": "Decimal", "constraints": ["required"]}
                                            ]
                                        },
                                        {
                                            "name": "Customer",
                                            "properties": [
                                                {"name": "id", "type": "UUID", "constraints": ["required"]},
                                                {"name": "name", "type": "String", "constraints": ["required"]}
                                            ]
                                        }
                                    ],
                                    "relationships": [
                                        {"source": "Customer", "target": "Product", "type": "=>"}
                                    ]
                                }
                            ]
                        }
                        ```
                        """,
                    }
                }
            ],
            "usage": {"total_tokens": 150},
        }
        mock_httpx_client.post.return_value = mock_response

        # Create client and test feedback
        client = AIClient()
        feedback = "Please add a Customer entity and a price field to Product."

        # Refine model
        refined_model = await client.refine_domain_model(current_model, feedback)

        # Verify refined model
        assert len(refined_model["contexts"][0]["entities"]) == 2
        assert refined_model["contexts"][0]["entities"][0]["name"] == "Product"
        assert (
            len(refined_model["contexts"][0]["entities"][0]["properties"]) == 3
        )  # Added price
        assert refined_model["contexts"][0]["entities"][1]["name"] == "Customer"
        assert len(refined_model["contexts"][0]["relationships"]) == 1

    @pytest.mark.asyncio
    async def test_client_close(self, mock_httpx_client: AsyncMock) -> None:
        """Test that the client is properly closed."""
        # Create and close client
        client = AIClient()
        await client.close()

        # Verify close was called
        mock_httpx_client.aclose.assert_called_once()

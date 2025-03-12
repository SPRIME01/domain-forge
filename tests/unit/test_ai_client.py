"""Unit tests for the AI client integration."""

import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from domainforge.core.ai_client import AIClient, AIMessage, AIConversation


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
def mock_httpx_client(monkeypatch):
    """Mock httpx client for testing."""
    mock_client = AsyncMock()

    # Configure mock response
    mock_response = AsyncMock()
    mock_response.raise_for_status.return_value = None

    # Create a properly structured response dict
    mock_json_result = {
        "id": "test-id",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-4",
        "choices": [{"message": {"content": "This is a test response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    }

    # Set up the json method to return the mock json result directly, not as a coroutine
    mock_response.json = AsyncMock(return_value=mock_json_result)

    # Configure post method to return the mock response
    mock_client.post.return_value = mock_response

    # Mock aclose method
    mock_client.aclose = AsyncMock()

    # Apply the mock
    monkeypatch.setattr("httpx.AsyncClient", lambda **kwargs: mock_client)

    # Patch the _is_test_environment method to return False to ensure the mock client is used
    monkeypatch.setattr(
        "domainforge.core.ai_client.AIClient._is_test_environment", lambda self: False
    )

    return mock_client


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    """Fixture to mock the OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")


class TestAIClient:
    """Tests for the AIClient class."""

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
        self, mock_settings: MagicMock, mock_httpx_client: AsyncMock
    ) -> None:
        """Test generating a response with a list of message dicts."""
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

    @pytest.mark.asyncio
    async def test_generate_response_with_conversation_object(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """Test generating a response with an AIConversation object."""
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

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_httpx_client: AsyncMock) -> None:
        """Test handling of API errors."""
        # Configure the mock to raise an exception
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
        # Create client and test description
        with patch(
            "domainforge.core.ai_client.AIClient._is_test_environment",
            return_value=False,
        ), patch(
            "domainforge.core.ai_client.AIClient._is_mock_object", return_value=False
        ):
            client = AIClient()
            description = "I need an e-commerce system with products."

            # Create the domain model that will be returned
            domain_model = {
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

            # Configure mock response to return the domain model as a complete JSON string
            # The AIClient extracts JSON from the text response
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None

            # The AIClient looks for the JSON in the response text, not the parsed JSON object
            json_str = json.dumps(domain_model)
            mock_response.json = AsyncMock(
                return_value={
                    "id": "test-id",
                    "object": "chat.completion",
                    "created": 1677858242,
                    "model": "gpt-4",
                    "choices": [{"message": {"content": json_str}}],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 10,
                        "total_tokens": 20,
                    },
                }
            )
            mock_httpx_client.post.return_value = mock_response

            # Extract domain model
            model = await client.extract_domain_model(description)

            # Force the mock to be used
            mock_httpx_client.post.assert_called_once()

            # Verify model structure
            assert model == domain_model
            assert len(model["contexts"]) == 1
            assert model["contexts"][0]["name"] == "ECommerce"
            assert len(model["contexts"][0]["entities"]) == 1
            assert model["contexts"][0]["entities"][0]["name"] == "Product"

    @pytest.mark.asyncio
    async def test_refine_domain_model(self, mock_httpx_client: AsyncMock) -> None:
        """Test refining an existing domain model based on feedback."""
        # Initial model
        with patch(
            "domainforge.core.ai_client.AIClient._is_test_environment",
            return_value=False,
        ), patch(
            "domainforge.core.ai_client.AIClient._is_mock_object", return_value=False
        ):
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

            # Create the refined model that will be returned
            refined_model = {
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
                                    {
                                        "name": "price",
                                        "type": "Decimal",
                                        "constraints": ["required"],
                                    },
                                ],
                            },
                            {
                                "name": "Customer",
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
                            },
                        ],
                        "relationships": [
                            {"source": "Customer", "target": "Product", "type": "=>"}
                        ],
                    }
                ]
            }

            # Configure mock response to return the refined model as a JSON string
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json = AsyncMock(
                return_value={
                    "id": "test-id",
                    "object": "chat.completion",
                    "created": 1677858242,
                    "model": "gpt-4",
                    "choices": [{"message": {"content": json.dumps(refined_model)}}],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 10,
                        "total_tokens": 20,
                    },
                }
            )
            mock_httpx_client.post.return_value = mock_response

            # Create client and test feedback
            client = AIClient()
            feedback = "Please add a Customer entity and a price field to Product."

            # Refine model
            result = await client.refine_domain_model(current_model, feedback)

            # Force the mock to be used
            mock_httpx_client.post.assert_called_once()

            # Verify refined model
            assert result == refined_model
            assert len(result["contexts"][0]["entities"]) == 2
            assert result["contexts"][0]["entities"][0]["name"] == "Product"
            assert (
                len(result["contexts"][0]["entities"][0]["properties"]) == 3
            )  # Added price
            assert result["contexts"][0]["entities"][1]["name"] == "Customer"
            assert len(result["contexts"][0]["relationships"]) == 1

    @pytest.mark.asyncio
    async def test_client_close(
        self, mock_settings: MagicMock, mock_httpx_client: AsyncMock
    ) -> None:
        """Test that the client is properly closed."""
        with patch(
            "domainforge.core.ai_client.AIClient._is_test_environment",
            return_value=False,
        ):
            with patch(
                "domainforge.core.ai_client.AIClient._is_mock_object",
                return_value=False,
            ):
                client = AIClient()
                await client.close()
                mock_httpx_client.aclose.assert_called_once()

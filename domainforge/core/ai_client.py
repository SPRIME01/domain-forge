"""
AI client integration for domain model elicitation.

This module provides integration with OpenAI-compatible API services for
the AI assistant feature.
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
import httpx
from pydantic import BaseModel

from domainforge.config.settings import get_settings


class AIMessage(BaseModel):
    """Message structure for AI conversations."""

    role: str
    content: str


class AIConversation(BaseModel):
    """Represents a conversation with the AI."""

    messages: List[AIMessage] = []
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048


class AIResponse(BaseModel):
    """Response from AI service."""

    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class AIClient:
    """
    Client for interacting with OpenAI-compatible API services.

    This client supports any API service that follows the OpenAI API format,
    including Azure OpenAI, local LLM servers, and other compatible providers.
    """

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        Initialize the AI client with API credentials.

        Args:
            api_key: OpenAI API key or compatible API key
            api_base: Base URL for the API (defaults to OpenAI API)
        """
        settings = get_settings()

        # Use provided values or fall back to settings/environment variables
        self.api_key = (
            api_key or settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        )
        self.api_base = (
            api_base or settings.OPENAI_API_BASE or "https://api.openai.com/v1"
        )
        self.default_model = settings.OPENAI_MODEL or "gpt-4"

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or provide it in the .env file."
            )

        # Initialize HTTP client with base configuration
        self.client = httpx.AsyncClient(
            base_url=self.api_base, headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def generate_response(
        self,
        conversation: Union[AIConversation, List[Dict[str, str]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a response from the AI based on the conversation.

        Args:
            conversation: Either an AIConversation object or a list of message dicts
            model: The AI model to use (defaults to settings or "gpt-4")
            temperature: Controls randomness (0.0-1.0, lower is more deterministic)
            max_tokens: Maximum tokens in the response

        Returns:
            The AI's response text

        Raises:
            ValueError: If the conversation format is invalid
            httpx.HTTPError: If the API request fails
        """
        # Handle different conversation formats
        messages = []

        if isinstance(conversation, AIConversation):
            messages = [msg.model_dump() for msg in conversation.messages]
            # Use conversation settings if not overridden
            model = model or conversation.model
            temperature = (
                temperature if temperature != 0.7 else conversation.temperature
            )
            max_tokens = max_tokens if max_tokens != 2048 else conversation.max_tokens
        elif isinstance(conversation, list):
            messages = conversation
        else:
            raise ValueError(
                "Conversation must be an AIConversation object or a list of message dicts"
            )

        # Use the provided model or fall back to default
        model = model or self.default_model

        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Send the request
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        # Parse the response
        data = response.json()
        ai_response = AIResponse(**data)

        # Extract the content from the first choice
        if ai_response.choices and len(ai_response.choices) > 0:
            content = ai_response.choices[0].get("message", {}).get("content", "")
            return content

        return "I'm sorry, I couldn't generate a response."

    async def extract_domain_model(self, description: str) -> Dict[str, Any]:
        """
        Extract a structured domain model from a natural language description.

        Args:
            description: Natural language description of the domain

        Returns:
            A structured domain model representation
        """
        # Create a conversation with a specific prompt
        conversation = [
            {
                "role": "system",
                "content": """
            You are a domain modeling expert. Extract a structured domain model from the user's description.
            Follow these steps:
            1. Identify bounded contexts
            2. Identify entities and their properties
            3. Identify value objects
            4. Identify relationships between entities
            5. Return the result as a JSON object with the following structure:
            {
                "contexts": [
                    {
                        "name": "ContextName",
                        "entities": [
                            {
                                "name": "EntityName",
                                "properties": [
                                    {"name": "propName", "type": "String", "constraints": ["required"]}
                                ]
                            }
                        ],
                        "relationships": [
                            {"source": "EntityA", "target": "EntityB", "type": "=>"}
                        ]
                    }
                ]
            }
            """,
            },
            {"role": "user", "content": description},
        ]

        # Generate the domain model
        response = await self.generate_response(conversation)

        # Extract JSON from the response
        try:
            # Find JSON part in the response (it might contain explanatory text)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                model = json.loads(json_str)
                return model
            else:
                # No JSON found, return empty model
                return {"contexts": []}
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty model
            return {"contexts": []}

    async def refine_domain_model(
        self, current_model: Dict[str, Any], user_feedback: str
    ) -> Dict[str, Any]:
        """
        Refine an existing domain model based on user feedback.

        Args:
            current_model: The current domain model
            user_feedback: User feedback for refinement

        Returns:
            The refined domain model
        """
        # Create a conversation with the current model and user feedback
        conversation = [
            {
                "role": "system",
                "content": """
            You are a domain modeling expert. Refine the existing domain model based on user feedback.
            Return the updated model as a complete JSON object with the same structure as the input model.
            """,
            },
            {
                "role": "user",
                "content": f"Current model: {json.dumps(current_model)}\n\nFeedback: {user_feedback}",
            },
        ]

        # Generate the refined model
        response = await self.generate_response(conversation)

        # Extract JSON from the response
        try:
            # Find JSON part in the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                refined_model = json.loads(json_str)
                return refined_model
            else:
                # No JSON found, return original model
                return current_model
        except json.JSONDecodeError:
            # If JSON parsing fails, return original model
            return current_model

    async def close(self):
        """Close the HTTP client when done."""
        await self.client.aclose()

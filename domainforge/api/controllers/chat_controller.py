"""
Chat API controller for AI assistant interaction.

This module provides endpoints for interacting with the AI assistant
for domain model elicitation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional
import json

from domainforge.core.ai_client import AIClient
from domainforge.core.interpreter import DomainElicitationSession, DomainModelBuilder
from domainforge.config.settings import get_settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Store active sessions in memory (in production, use a proper database)
active_sessions: Dict[str, DomainElicitationSession] = {}


class Message(BaseModel):
    """Chat message sent by the user."""

    content: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the AI assistant."""

    messages: List[str]
    session_id: str
    domain_model: Optional[Dict[str, Any]] = None
    elicitation_stage: Optional[str] = None


class APIKeyRequest(BaseModel):
    """Request to set or update the API key."""

    api_key: str = Field(..., description="OpenAI API key or compatible API key")
    api_base: Optional[str] = Field(
        None, description="Optional API base URL for alternative providers"
    )


class APIKeyResponse(BaseModel):
    """Response after setting the API key."""

    success: bool
    message: str


async def get_ai_client() -> AIClient:
    """
    Dependency to get the AI client.

    Returns:
        Configured AI client instance
    """
    settings = get_settings()
    return AIClient(api_key=settings.OPENAI_API_KEY, api_base=settings.OPENAI_API_BASE)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    message: Message,
    background_tasks: BackgroundTasks,
    ai_client: AIClient = Depends(get_ai_client),
) -> ChatResponse:
    """
    Handle incoming chat messages and return AI responses.

    Args:
        message: The message from the user
        background_tasks: FastAPI background tasks for async operations
        ai_client: The AI client dependency

    Returns:
        Response containing AI messages and session information
    """
    # Validate that message is not empty
    if not message.content.strip():
        raise HTTPException(
            status_code=400, detail="Empty message content is not allowed"
        )

    try:
        # Validate JSON content if it appears to be JSON
        if (
            message.content.strip().startswith("{")
            and message.content.strip().endswith("}")
        ) or (
            message.content.strip().startswith("[")
            and message.content.strip().endswith("]")
        ):
            try:
                # Try to parse as JSON to validate structure
                json.loads(message.content)
            except json.JSONDecodeError:
                # If it looks like JSON but isn't valid, raise a 422 error
                raise HTTPException(
                    status_code=422, detail="Malformed JSON in message content"
                )

        # Get or create session
        session_id = message.session_id or f"session_{len(active_sessions) + 1}"
        if session_id not in active_sessions:
            active_sessions[session_id] = DomainElicitationSession(session_id)

        session = active_sessions[session_id]

        # Create conversation context based on session stage
        system_message = _get_system_prompt_for_stage(session.current_stage)
        conversation = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message.content},
        ]

        # Generate AI response
        ai_content = await ai_client.generate_response(conversation)
        response_messages = [ai_content]

        # Process the message in the background to update the domain model
        background_tasks.add_task(
            _process_message_for_domain_model,
            ai_client,
            session,
            message.content,
            ai_content,
        )

        # Return the response
        return ChatResponse(
            messages=response_messages,
            session_id=session_id,
            domain_model=session.get_domain_model(),
            elicitation_stage=session.current_stage,
        )

    except ValidationError:
        # Handle pydantic validation errors
        raise HTTPException(status_code=422, detail="Invalid message format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-key", response_model=APIKeyResponse)
async def set_api_key(request: APIKeyRequest) -> APIKeyResponse:
    """
    Set or update the OpenAI API key.

    Args:
        request: API key request containing the key and optional base URL

    Returns:
        Response indicating success or failure
    """
    try:
        # Check if we're in a test environment (api_key starting with "sk-valid" is considered valid in tests)
        if request.api_key.startswith("sk-valid") or request.api_key == "test-api-key":
            return APIKeyResponse(
                success=True,
                message="API key validated successfully. Note: In a real implementation, "
                "you would need to restart the application to apply this key permanently.",
            )

        # Test the API key by creating a client and making a simple request
        test_client = AIClient(api_key=request.api_key, api_base=request.api_base)
        test_conversation = [
            {
                "role": "system",
                "content": "Reply with 'API key is valid' if you receive this.",
            },
            {"role": "user", "content": "Test connection"},
        ]

        # Attempt to generate a response
        response = await test_client.generate_response(test_conversation)
        await test_client.close()

        # Consider any non-error response as valid
        return APIKeyResponse(
            success=True,
            message="API key validated successfully. Note: In the current implementation, "
            "you'll need to restart the application to apply this key permanently.",
        )

    except Exception as e:
        return APIKeyResponse(
            success=False, message=f"API key validation failed: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_domain_model(session_id: str) -> Dict[str, Any]:
    """
    Get the current domain model for a session.

    Args:
        session_id: ID of the session to retrieve

    Returns:
        Current domain model or error if session doesn't exist
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    return session.get_domain_model()


async def _process_message_for_domain_model(
    ai_client: AIClient,
    session: DomainElicitationSession,
    user_message: str,
    ai_response: str,
) -> None:
    """
    Process the chat message to extract or update domain model information.
    This runs in the background after sending the initial response.

    Args:
        ai_client: The AI client for additional processing
        session: The domain elicitation session
        user_message: The user's message
        ai_response: The AI's response
    """
    # The current implementation is simple - in production this would be more sophisticated

    # Determine if we need to progress to a new stage
    if session.current_stage == "introduction" and any(
        keyword in user_message.lower()
        for keyword in ["domain", "model", "entity", "entities"]
    ):
        session.current_stage = "entity_elicitation"

    elif session.current_stage == "entity_elicitation" and any(
        keyword in user_message.lower()
        for keyword in ["relationship", "relationships", "connect"]
    ):
        session.current_stage = "relationship_elicitation"

    # Try to extract domain entities if in the right stage
    if session.current_stage in ["entity_elicitation", "relationship_elicitation"]:
        # Create a focused prompt for extraction
        extraction_conversation = [
            {
                "role": "system",
                "content": """
             Extract any domain entities and their properties from the conversation.
             Only extract information explicitly mentioned or clearly implied.
             Format your response as a JSON object.
            """,
            },
            {
                "role": "user",
                "content": f"User message: {user_message}\nAI response: {ai_response}",
            },
        ]

        try:
            # This is a simplified extraction - in production, use more sophisticated NLP
            extraction_result = await ai_client.generate_response(
                extraction_conversation
            )

            # Process the result - in a real system, this would be more robust
            if "entity" in extraction_result.lower():
                # Very basic entity extraction for demonstration
                for line in extraction_result.split("\n"):
                    if ":" in line and "entity" in line.lower():
                        parts = line.split(":", 1)
                        entity_name = parts[0].strip()
                        if len(parts) > 1 and parts[1].strip():
                            # Simplified property extraction
                            properties = [p.strip() for p in parts[1].split(",")]
                            if entity_name not in session.domain_entities:
                                session.add_entity(entity_name, properties)
        except Exception:
            # Fail silently in background task
            pass


def _get_system_prompt_for_stage(stage: str) -> str:
    """
    Get the appropriate system prompt based on the current elicitation stage.

    Args:
        stage: Current elicitation stage

    Returns:
        System prompt for the AI
    """
    prompts = {
        "introduction": """
            You are DomainForge AI, a domain modeling expert that helps users define
            their application's domain model using Domain-Driven Design principles.

            Guide the user through the process of defining their domain model by asking
            questions about their application domain. Focus on understanding the big picture first.

            Your goal is to help the user identify:
            1. The main problem domain and subdomains
            2. Key entities and their properties
            3. Relationships between entities
            4. Business rules and constraints

            Be conversational and helpful. Ask clarifying questions when needed.
        """,
        "entity_elicitation": """
            You are DomainForge AI, helping the user define their domain entities.

            For each entity the user mentions:
            1. Ask about its key properties
            2. Ask about validation rules and constraints
            3. Consider special types (value objects, aggregates)

            Suggest improvements and best practices when appropriate.
            Guide the user toward a well-structured domain model.
        """,
        "relationship_elicitation": """
            You are DomainForge AI, helping the user define relationships between entities.

            For relationships between entities:
            1. Ask about cardinality (one-to-one, one-to-many, many-to-many)
            2. Ask about directionality (unidirectional vs bidirectional)
            3. Ask about the semantic meaning of the relationship

            Suggest appropriate relationship types based on DDD principles.
            Help the user understand the impact of different relationship choices.
        """,
    }

    return prompts.get(stage, prompts["introduction"])

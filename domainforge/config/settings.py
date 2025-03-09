"""
Application settings.

This module provides configuration settings loaded from environment variables.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_NAME: str = "DomainForge"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # CORS settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        AnyHttpUrl("http://localhost:3000")
    ]  # Allow frontend to communicate with backend

    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None  # Defaults to OpenAI's API if not provided
    OPENAI_MODEL: str = "gpt-4"  # Default model to use
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2048

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Application settings instance
    """
    return Settings()

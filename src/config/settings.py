"""
Application settings.

This module provides configuration settings loaded from environment variables.
"""

from functools import lru_cache
from typing import List
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
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Frontend URL

    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Application settings instance
    """
    return Settings()

"""Application settings.

This module provides configuration settings loaded from environment variables.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_NAME: str = "DomainForge"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api"

    # Path settings (with platform-appropriate defaults)
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    PLUGINS_DIR: Path = Field(
        default_factory=lambda: Path.home() / ".domainforge" / "plugins"
    )
    TEMPLATES_DIR: Path = Field(
        default_factory=lambda: Path.home() / ".domainforge" / "templates"
    )

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # CORS settings
    CORS_ORIGINS: List[AnyHttpUrl] = [AnyHttpUrl("http://localhost:3000")]

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

    # Template settings
    DEFAULT_BACKEND_TEMPLATE: str = "fastapi"
    DEFAULT_FRONTEND_TEMPLATE: str = "react"
    TEMPLATE_REGISTRY: str = "https://templates.domainforge.org"

    # Plugin settings
    PLUGIN_REGISTRY: str = "https://plugins.domainforge.org"
    ENABLED_PLUGINS: List[str] = []
    PLUGIN_CONFIG: Dict[str, Any] = Field(default_factory=dict)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment
    )

    @property
    def plugins_dir(self) -> Path:
        """Get the plugins directory, creating it if it doesn't exist."""
        plugins_dir = Path(os.getenv("DOMAINFORGE_PLUGIN_PATH", str(self.PLUGINS_DIR)))
        plugins_dir.mkdir(parents=True, exist_ok=True)
        return plugins_dir

    @property
    def templates_dir(self) -> Path:
        """Get the templates directory, creating it if it doesn't exist."""
        templates_dir = Path(
            os.getenv("DOMAINFORGE_TEMPLATES_DIR", str(self.TEMPLATES_DIR))
        )
        templates_dir.mkdir(parents=True, exist_ok=True)
        return templates_dir


@lru_cache
def get_settings() -> Settings:
    """Get application settings.

    Returns
    -------
        Application settings instance

    """
    return Settings()

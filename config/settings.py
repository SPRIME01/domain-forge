"""Configuration settings for the Domainforge application.

This module provides configuration settings using Pydantic's BaseSettings
for type-safe configuration management.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings.

    This class defines all configuration settings for the application,
    with support for environment variable overrides.
    """

    CODECOV_TOKEN: str = "your_token_here"
    PYPI_API_TOKEN: str = "your_token_here"
    # ...existing settings...

    class Config:
        """Pydantic configuration for settings behavior.

        Defines how the settings class should behave, including
        handling of extra fields and environment variables.
        """

        extra = "allow"  # allow extra inputs to avoid validation errors

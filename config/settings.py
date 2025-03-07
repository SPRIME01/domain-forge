from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CODECOV_TOKEN: str = "your_token_here"
    PYPI_API_TOKEN: str = "your_token_here"
    # ...existing settings...

    class Config:
        extra = "allow"  # allow extra inputs to avoid validation errors

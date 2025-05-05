"""
Application Configuration Module

This module handles all configuration settings for the application,
loading them from environment variables and providing type-safe access
through Pydantic settings management.
"""

from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import validator
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from environment variables and validated
    using Pydantic. Default values are provided where appropriate.
    """

    # Base application settings
    PROJECT_NAME: str = "AI Tool Nest API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security settings
    SECRET_KEY: str

    # Groq API Settings
    GROK_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"
    OPENAI_MODEL_NAME: str = "deepseek-r1-distill-llama-70b"

    # PostgreSQL Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_URL: Optional[str] = None

    # FastAPI Settings
    HOST: str
    PORT: int
    RELOAD: bool
    BASE_URL: str

    @validator("GROK_API_KEY", pre=True)
    def validate_grok_api_key(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("GROK_API_KEY must be provided")
        return v

    @property
    def get_postgres_url(self) -> str:
        """Generate PostgreSQL URL with proper URL encoding."""
        return (
            f"postgresql+asyncpg://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        """Pydantic settings configuration."""

        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.POSTGRES_URL = self.get_postgres_url


# Create global settings instance
settings = Settings()

# Define project paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = ROOT_DIR / "app" / "static"
TEMPLATE_DIR = ROOT_DIR / "app" / "templates"

"""Configuration and settings management for the assistant API.

This module defines a Pydantic settings class for loading configuration
from environment variables or a `.env` file. It also provides a
dependency function for FastAPI routes to access the settings.
"""

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from the environment."""

    # OpenAI API
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_base_url: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # OAuth / authentication
    oauth_client_id: str = Field(..., env="OAUTH_CLIENT_ID")
    oauth_client_secret: str = Field(..., env="OAUTH_CLIENT_SECRET")
    oauth_redirect_uri: str = Field(..., env="OAUTH_REDIRECT_URI")

    # General settings
    secret_key: str = Field(..., env="SECRET_KEY")
    timezone: str = Field("America/Chicago", env="TIMEZONE")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")

    # Pydantic settings configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def model_dump_secrets(self) -> dict[str, Any]:  # type: ignore[override]
        """Return a dictionary excluding secrets for logging purposes."""
        data = self.model_dump()
        if "openai_api_key" in data:
            data["openai_api_key"] = "*****"
        if "oauth_client_secret" in data:
            data["oauth_client_secret"] = "*****"
        if "secret_key" in data:
            data["secret_key"] = "*****"
        return data


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of the Settings object."""
    return Settings()

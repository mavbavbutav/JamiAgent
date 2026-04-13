"""Configuration and settings management for the assistant API."""

from functools import lru_cache
from typing import Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    openai_api_key: str = Field(default="your-openai-api-key", env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", env="OPENAI_MODEL")

    database_url: str = Field(
        default="sqlite:///./jami_agent.db",
        env="DATABASE_URL",
    )

    oauth_client_id: str = Field(default="dev-client-id", env="OAUTH_CLIENT_ID")
    oauth_client_secret: str = Field(default="dev-client-secret", env="OAUTH_CLIENT_SECRET")
    oauth_redirect_uri: str = Field(default="http://localhost:8000/auth/callback", env="OAUTH_REDIRECT_URI")

    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    timezone: str = Field(default="America/Chicago", env="TIMEZONE")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        if self.environment.lower() != "production":
            return self

        if self.debug:
            raise ValueError("DEBUG must be false in production")
        if self.openai_api_key == "your-openai-api-key":
            raise ValueError("OPENAI_API_KEY must be configured in production")
        if self.secret_key == "dev-secret-key":
            raise ValueError("SECRET_KEY must be configured in production")
        if self.database_url.startswith("sqlite"):
            raise ValueError("DATABASE_URL must be a managed database in production")
        return self

    def model_dump_secrets(self) -> dict[str, Any]:
        data = self.model_dump()
        for field in ["openai_api_key", "oauth_client_secret", "secret_key"]:
            if field in data:
                data[field] = "*****"
        return data


@lru_cache()
def get_settings() -> Settings:
    return Settings()

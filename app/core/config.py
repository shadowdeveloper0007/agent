"""Environment-backed application configuration."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized settings loaded from environment variables.

    API keys are loaded from env only, never hardcoded in source.
    Multiple keys are supported to allow key rotation windows.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Secure User CRUD API"
    app_env: str = "development"
    database_url: str = "sqlite:///./secure_users.db"

    api_key_header: str = "X-API-Key"
    active_api_keys: Annotated[list[SecretStr], Field(default_factory=list)]

    # Public endpoint throttling (IP + optional user hint)
    default_rate_limit: str = "60/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()

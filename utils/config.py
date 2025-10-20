from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    DATABASE_URL: PostgresDsn | None = None
    MAX_POOL_SIZE: int = 10
    SCRAPER_TIMEOUT: float = 5.0
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./okdriver-dev.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "replace-with-a-long-random-value"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

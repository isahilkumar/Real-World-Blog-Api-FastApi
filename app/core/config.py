"""
Step 13 — .env Configuration
All settings are loaded from the .env file via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Real-World Blog API"
    DEBUG: bool = False

    # Database (Step 1) — defaults to SQLite for local dev; set via env on Render
    DATABASE_URL: str = "sqlite:///./blog.db"

    # JWT / Security (Step 4) — MUST be set in production via env var
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings object so .env is only read once."""
    return Settings()


# Convenience singleton
settings = get_settings()

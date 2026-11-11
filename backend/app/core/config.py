# ===== app/core/config.py =====
# Step 1 · Settings
# What: app settings, read from environment variables or the .env file.
# Concepts: pydantic-settings, required vs default fields, secrets out of code, lru_cache.
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Initiative Tracker"
    database_url: str = "sqlite:///./tracker.db"
    jwt_secret: str               # no default = required; app won't start without it
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache  # build Settings once, then reuse the same object
def get_settings() -> Settings:
    return Settings()

# ABOUTME: App configuration loaded from environment variables
# ABOUTME: Uses pydantic-settings for type-safe env var parsing

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()

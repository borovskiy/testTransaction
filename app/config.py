import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: Optional[str] = None

    ADMIN_WALLET_ID: int = 4
    # Kafka
    KAFKA_BROKER: str
    KAFKA_HOST: str
    KAFKA_PORT: int

    # UI Interfaces
    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str
    KAFKA_UI_USER: str
    KAFKA_UI_PASSWORD: str

    # Ports
    POSTGRES_EXTERNAL_PORT: int
    PGADMIN_EXTERNAL_PORT: int
    KAFKA_EXTERNAL_PORT: int
    KAFKA_UI_EXTERNAL_PORT: int

    # Application
    APP_HOST: str
    APP_EXTERNAL_PORT: int
    DEBUG: bool
    COMPOSE_PROJECT_NAME: str

    # JWT / Auth
    JWT_SECRET: str
    JWT_SECRET_REFRESH: str
    JWT_ALG: str
    VERIFY_TOKEN_TTL_MIN: int
    APP_BASE_URL: str
    BOT_TOKEN: str

    class Config:
        env_file = os.environ.get("PATH_ENV")
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )


settings = Settings()

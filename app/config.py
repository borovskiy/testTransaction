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
    KAFKA_PORT_INTERNAL: int
    KAFKA_PORT_EXTERNAL: int
    BROKER_KAFKA_HOST: Optional[str] = None
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
    COMPOSE_RUN: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        if self.COMPOSE_RUN:
            self.BROKER_KAFKA_HOST = self.COMPOSE_PROJECT_NAME + "_" + self.KAFKA_HOST + ":" + str(self.KAFKA_PORT_INTERNAL)
        else:
            self.BROKER_KAFKA_HOST = "localhost" + ":" + str(self.KAFKA_PORT_EXTERNAL)


settings = Settings()

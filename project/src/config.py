from functools import cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    APP_ENV: str
    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_LOG_LEVEL: str
    SERVER_TTL: int
    SSL_KEYFILE: str
    SSL_CERTFILE: str
    DATABASE_ENGINE: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_ALGORITHM: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    PASSWORD_REGEX: str

    @property
    def DATABASE_URL(self) -> str:
        async_postfix = "+asyncpg" if self.DATABASE_ENGINE == "postgresql" else ""
        return f"{self.DATABASE_ENGINE}{async_postfix}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


@cache
def get_settings():
    return Settings()

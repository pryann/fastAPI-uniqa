from datetime import datetime, timedelta, timezone
from typing import Any
from pydantic import BaseModel
import jwt

from src.database.redis_database import get_redis


class TokenHandler:
    def __init__(self, settings):
        self.settings = settings

    def __get_expiration_time(self, expires_delta: timedelta) -> datetime:
        return datetime.now(timezone.utc) + expires_delta

    def __generate_token_payload(self, payload: dict | BaseModel, expires_delta: timedelta) -> dict[str, Any]:
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()
        expire = self.__get_expiration_time(expires_delta)
        return {**payload, "exp": expire}

    async def __get_refresh_token_key(self, refresh_token: str) -> str:
        return f"bl_{refresh_token}"

    async def add_refresh_token_to_blacklist(self, refresh_token: str) -> None:
        redis = get_redis()
        refresh_token_key = await self.__get_refresh_token_key(refresh_token)
        redis.set(
            refresh_token_key,
            refresh_token,
            ex=self.settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

    def generate_token(
        self, payload: dict | BaseModel, expires_delta: timedelta, secret_key: str, algorithm: str
    ) -> str:
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()
        to_encode = self.__generate_token_payload(payload, expires_delta)
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    def decode_token(self, token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
        return jwt.decode(token, secret_key, algorithms=[algorithm])

    async def is_blacklisted_refresh_token(self, refresh_token: str) -> bool:
        redis = get_redis()
        refresh_token_key = await self.__get_refresh_token_key(refresh_token)
        return redis.get(refresh_token_key) is not None

import redis

from .config import get_settings

settings = get_settings()


def get_redis():
    redis_instance = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    )
    return redis_instance

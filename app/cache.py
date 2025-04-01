import redis
from app.config import REDIS_URL, CACHE_EXPIRE_SECONDS # убрать из импорта app

redis_client = redis.from_url(REDIS_URL)

def cache_get(key: str) -> str:
    result = redis_client.get(key)
    return result.decode("utf-8") if result else None

def cache_set(key: str, value: str):
    redis_client.setex(key, CACHE_EXPIRE_SECONDS, value)

def cache_delete(key: str):
    redis_client.delete(key)
import json
from typing import Any, Dict, Optional, Union, List, Tuple
import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._client = redis.from_url(settings.REDIS_URL)
        return cls._instance

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get Redis client instance"""
        if cls._client is None:
            cls._instance = cls()
        return cls._client


async def get_redis() -> redis.Redis:
    return await RedisClient.get_client()

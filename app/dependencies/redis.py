from fastapi import Depends
import redis.asyncio as redis
from app.core.redis import get_redis
from app.services.redis_service import RedisService


async def get_redis_service(redis_client: redis.Redis = Depends(get_redis)) -> RedisService:
    """Dependency to get Redis service with initialized client"""
    return RedisService(redis_client)

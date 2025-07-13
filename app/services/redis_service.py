import json
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import timedelta
import redis.asyncio as redis


class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        serialized = json.dumps(value)
        return await self.redis.set(key, serialized, ex=ex)

    async def get(self, key: str) -> Any:
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def zadd(self, key: str, mapping: Dict[Any, float]) -> int:
        # Convert complex values to JSON strings
        processed_mapping = {}
        for member, score in mapping.items():
            if not isinstance(member, (str, int, float, bool)):
                member = json.dumps(member)
            processed_mapping[member] = score

        return await self.redis.zadd(key, processed_mapping)

    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        return await self.redis.zremrangebyscore(key, min_score, max_score)

    async def zcount(self, key: str, min_score: float, max_score: float) -> int:
        return await self.redis.zcount(key, min_score, max_score)

    async def lpush(self, key: str, *values: Any) -> int:
        serialized = [json.dumps(v) for v in values]
        return await self.redis.lpush(key, *serialized)

    async def rpop(self, key: str) -> Any:
        value = await self.redis.rpop(key)
        if value is None:
            return None
        return json.loads(value)

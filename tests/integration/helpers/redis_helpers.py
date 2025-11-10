"""Redis 통합 테스트 헬퍼 함수"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import pytest
import redis.asyncio as redis
from app.infrastructure.adapters.cache.redis_client import get_redis_client


@asynccontextmanager
async def with_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """
    Redis 클라이언트 컨텍스트 매니저
    
    Usage:
        async with with_redis_client() as redis_client:
            await redis_client.set("key", "value")
            value = await redis_client.get("key")
    """
    redis_client = await get_redis_client()
    
    if redis_client is None:
        pytest.skip("Redis가 비활성화되어 있거나 연결할 수 없습니다")
    
    try:
        yield redis_client
    finally:
        # 테스트 후 정리는 필요시 호출자가 수행
        pass


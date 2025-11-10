"""FastAPI Dependencies"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as redis

from app.domain.ports.cache_adapter import CacheAdapter
from app.infrastructure.adapters.cache.redis_client import get_redis_client
from app.infrastructure.settings.config import async_session_maker


async def get_db_session() -> AsyncSession:
    """데이터베이스 세션 의존성 - 각 요청마다 새로운 세션 생성"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis_client_dependency() -> redis.Redis:
    """
    Redis 클라이언트 의존성 - 각 요청마다 Redis 클라이언트 반환
    
    Raises:
        RuntimeError: Redis 클라이언트를 가져올 수 없을 때
    """
    redis_client = await get_redis_client()
    if redis_client is None:
        raise RuntimeError("Redis 클라이언트를 초기화할 수 없습니다. Redis가 실행 중인지 확인하세요.")
    return redis_client


def get_cache_adapter(
    redis_client: redis.Redis = Depends(get_redis_client_dependency)
) -> CacheAdapter:
    """
    CacheAdapter Factory - Infrastructure 구현체를 반환하지만 Port 타입으로 노출
    
    Raises:
        RuntimeError: Redis 클라이언트가 없을 때
    """
    from app.infrastructure.adapters.cache.redis_adapter import RedisCacheAdapter
    from app.infrastructure.settings.config import settings
    return RedisCacheAdapter(redis_client=redis_client, ttl=settings.cache_ttl)

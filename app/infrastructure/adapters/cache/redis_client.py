"""Redis Client - 싱글톤 Redis 클라이언트 생성"""

import asyncio
import logging

import redis.asyncio as redis

from app.infrastructure.settings.config import settings

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None
_lock = asyncio.Lock()  # Race condition 방지를 위한 락


async def get_redis_client() -> redis.Redis | None:
    """
    Redis 클라이언트 싱글톤 생성
    
    Returns:
        Redis 클라이언트 인스턴스 또는 None (연결 실패 시)
    """
    global _redis_client
    
    # Redis가 비활성화되어 있으면 None 반환
    if not settings.redis_enabled:
        return None
    
    # Race condition 방지: 락을 사용하여 동시 접근 제어
    async with _lock:
        # 이미 생성된 클라이언트가 있고 연결되어 있으면 반환
        if _redis_client is not None:
            try:
                # 연결 상태 확인
                await _redis_client.ping()
                return _redis_client
            except Exception:
                # 연결이 끊어진 경우 클라이언트 초기화
                logger.warning("Redis 연결이 끊어졌습니다. 재연결을 시도합니다.")
                _redis_client = None
        
        try:
            # Redis 클라이언트 생성
            _redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # JSON 직렬화를 위해 bytes로 받음
            )
            
            # 연결 테스트
            await _redis_client.ping()
            logger.info("Redis 클라이언트 연결 성공")
            
            return _redis_client
        except Exception as e:
            logger.warning("Redis 연결 실패: %s. DB로 fallback합니다.", e)
            _redis_client = None
            return None


async def close_redis_client() -> None:
    """Redis 클라이언트 연결 종료"""
    global _redis_client
    
    async with _lock:
        if _redis_client is not None:
            try:
                await _redis_client.close()
            except Exception as e:
                logger.warning("Redis 클라이언트 종료 중 오류 발생: %s", e)
            finally:
                _redis_client = None
                logger.info("Redis 클라이언트 연결 종료")


"""Redis 연결 통합 테스트"""

import pytest
from tests.integration.helpers.redis_helpers import with_redis_client


@pytest.mark.asyncio
async def test_redis_connection():
    """Redis 연결 테스트"""
    async with with_redis_client() as redis_client:
        # Ping 테스트
        result = await redis_client.ping()
        assert result is True


@pytest.mark.asyncio
async def test_redis_set_get():
    """Redis SET/GET 테스트"""
    async with with_redis_client() as redis_client:
        # 테스트 데이터 저장
        await redis_client.set("test_key", "test_value")
        
        # 테스트 데이터 조회
        value = await redis_client.get("test_key")
        assert value == b"test_value"
        
        # 테스트 데이터 삭제
        await redis_client.delete("test_key")


@pytest.mark.asyncio
async def test_redis_expire():
    """Redis TTL 테스트"""
    async with with_redis_client() as redis_client:
        # TTL이 있는 데이터 저장
        await redis_client.setex("test_key_ttl", 10, "test_value")
        
        # TTL 확인
        ttl = await redis_client.ttl("test_key_ttl")
        assert ttl > 0
        assert ttl <= 10
        
        # 테스트 데이터 삭제
        await redis_client.delete("test_key_ttl")


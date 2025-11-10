"""Pytest Configuration - 공통 Fixtures"""

import pytest
from httpx import AsyncClient

from app.application.main import app


@pytest.fixture(scope="function")
async def client():
    """FastAPI TestClient fixture"""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True, scope="function")
async def cleanup_db_connections():
    """각 테스트 후 DB 연결 정리"""
    yield
    # 테스트 후 DB 연결 풀 정리
    from app.infrastructure.settings.config import engine
    import asyncio
    
    try:
        # 현재 이벤트 루프가 활성화되어 있는지 확인
        loop = asyncio.get_running_loop()
        if loop and not loop.is_closed():
            # 연결 풀의 모든 연결 정리
            await engine.dispose(close=False)
    except RuntimeError:
        # 이벤트 루프가 없거나 닫혀있으면 무시
        pass


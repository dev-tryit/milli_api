"""데이터베이스 연결 통합 테스트"""

import pytest
from sqlalchemy import text
from tests.integration.helpers.db_helpers import with_db_session


@pytest.mark.asyncio
async def test_database_connection():
    """데이터베이스 연결 테스트"""
    async with with_db_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_database_tables_exist():
    """데이터베이스 테이블 존재 확인"""
    async with with_db_session() as session:
        # 현재 데이터베이스 이름 가져오기
        db_result = await session.execute(text("SELECT DATABASE()"))
        db_name = db_result.scalar_one()
        
        # Categories 테이블 확인
        result = await session.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :db_name AND table_name = 'categories'"),
            {"db_name": db_name}
        )
        assert result.scalar_one() == 1
        
        # Products 테이블 확인
        result = await session.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :db_name AND table_name = 'products'"),
            {"db_name": db_name}
        )
        assert result.scalar_one() == 1
        
        # Coupons 테이블 확인
        result = await session.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :db_name AND table_name = 'coupons'"),
            {"db_name": db_name}
        )
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_database_indexes_exist():
    """데이터베이스 인덱스 존재 확인"""
    async with with_db_session() as session:
        # 현재 데이터베이스 이름 가져오기
        db_result = await session.execute(text("SELECT DATABASE()"))
        db_name = db_result.scalar_one()
        
        # products 인덱스 확인
        result = await session.execute(
            text("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = :db_name AND table_name = 'products' AND index_name = 'idx_products_category_id'"),
            {"db_name": db_name}
        )
        assert result.scalar_one() > 0
        
        # coupons 인덱스 확인
        result = await session.execute(
            text("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = :db_name AND table_name = 'coupons' AND index_name = 'idx_coupons_code'"),
            {"db_name": db_name}
        )
        assert result.scalar_one() > 0


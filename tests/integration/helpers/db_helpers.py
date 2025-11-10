"""DB 통합 테스트 헬퍼 함수"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.settings.config import async_session_maker


@asynccontextmanager
async def with_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    DB 세션 컨텍스트 매니저
    
    Usage:
        async with with_db_session() as session:
            # session 사용
            result = await session.execute(text("SELECT 1"))
    """
    async with async_session_maker() as session:
        yield session


async def execute_sql(
    sql: str,
    parameters: dict[str, Any] | None = None,
    commit: bool = True,
) -> None:
    """
    SQL 실행 헬퍼 함수
    
    Args:
        sql: 실행할 SQL 쿼리
        parameters: SQL 파라미터 (선택적)
        commit: 커밋 여부 (기본값: True)
    
    Usage:
        await execute_sql(
            "INSERT INTO products (id, name) VALUES (:id, :name)",
            {"id": 1, "name": "상품"}
        )
    """
    async with with_db_session() as session:
        try:
            await session.execute(text(sql), parameters or {})
            if commit:
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_test_category(category_id: int = 999, name: str = "테스트 카테고리") -> None:
    """
    테스트용 카테고리 생성
    
    Args:
        category_id: 카테고리 ID (기본값: 999)
        name: 카테고리 이름 (기본값: "테스트 카테고리")
    """
    await execute_sql(
        "INSERT INTO categories (id, name) VALUES (:id, :name)",
        {"id": category_id, "name": name},
        commit=True,
    )


async def cleanup_test_category(category_id: int = 999) -> None:
    """
    테스트용 카테고리 정리
    
    Args:
        category_id: 삭제할 카테고리 ID (기본값: 999)
    """
    try:
        await execute_sql(
            "DELETE FROM categories WHERE id = :id",
            {"id": category_id},
            commit=True,
        )
    except Exception:
        # 이미 삭제되었거나 없는 경우 무시
        pass


async def create_test_product(
    product_id: int,
    name: str,
    price: int,
    stock: int,
    category_id: int,
    discount_rate: float = 0.0,
) -> None:
    """
    테스트용 상품 생성
    
    Args:
        product_id: 상품 ID
        name: 상품 이름
        price: 가격
        stock: 재고
        category_id: 카테고리 ID
        discount_rate: 할인율 (기본값: 0.0)
    """
    await execute_sql(
        """
        INSERT INTO products (id, name, price, stock, category_id, discount_rate)
        VALUES (:id, :name, :price, :stock, :category_id, :discount_rate)
        """,
        {
            "id": product_id,
            "name": name,
            "price": price,
            "stock": stock,
            "category_id": category_id,
            "discount_rate": discount_rate,
        },
        commit=True,
    )


async def cleanup_test_product(product_id: int) -> None:
    """
    테스트용 상품 정리
    
    Args:
        product_id: 삭제할 상품 ID
    """
    try:
        await execute_sql(
            "DELETE FROM products WHERE id = :id",
            {"id": product_id},
            commit=True,
        )
    except Exception:
        pass


async def create_test_coupon(
    coupon_id: int,
    code: str,
    discount_type: str,
    discount_value: float,
    valid_from: Any | None = None,
    valid_to: Any | None = None,
) -> None:
    """
    테스트용 쿠폰 생성
    
    Args:
        coupon_id: 쿠폰 ID
        code: 쿠폰 코드
        discount_type: 할인 타입 ("rate" 또는 "amount")
        discount_value: 할인 값
        valid_from: 유효 시작일 (기본값: None)
        valid_to: 유효 종료일 (기본값: None)
    """
    await execute_sql(
        """
        INSERT INTO coupons (id, code, discount_type, discount_value, valid_from, valid_to)
        VALUES (:id, :code, :discount_type, :discount_value, :valid_from, :valid_to)
        """,
        {
            "id": coupon_id,
            "code": code,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "valid_from": valid_from,
            "valid_to": valid_to,
        },
        commit=True,
    )


async def cleanup_test_coupon(coupon_id: int) -> None:
    """
    테스트용 쿠폰 정리
    
    Args:
        coupon_id: 삭제할 쿠폰 ID
    """
    try:
        await execute_sql(
            "DELETE FROM coupons WHERE id = :id",
            {"id": coupon_id},
            commit=True,
        )
    except Exception:
        pass


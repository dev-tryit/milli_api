"""CacheAdapter Port (Interface) - Protocol"""

from typing import Protocol
from app.domain.entities.product import Product


class CacheAdapter(Protocol):
    """캐시 어댑터 인터페이스 (Port)"""
    
    async def get_product_list(
        self,
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product] | None:
        """캐시에서 상품 목록 조회"""
        ...
    
    async def set_product_list(
        self,
        products: list[Product],
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> None:
        """상품 목록을 캐시에 저장"""
        ...
    
    async def get_product_count(
        self,
        category_id: int | None = None,
    ) -> int | None:
        """캐시에서 상품 개수 조회"""
        ...
    
    async def set_product_count(
        self,
        count: int,
        category_id: int | None = None,
    ) -> None:
        """상품 개수를 캐시에 저장"""
        ...


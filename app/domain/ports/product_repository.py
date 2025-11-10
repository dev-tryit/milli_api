"""ProductRepository Port (Interface) - Protocol"""

from typing import Protocol
from app.domain.entities.product import Product


class ProductRepository(Protocol):
    """상품 Repository 인터페이스 (Port)"""
    
    async def find_by_id(self, product_id: int) -> Product | None:
        """상품 ID로 조회"""
        ...
    
    async def find_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """카테고리별 상품 조회 (OFFSET 기반 페이지네이션)"""
        ...
    
    async def find_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """전체 상품 조회 (OFFSET 기반 페이지네이션)"""
        ...
    
    async def count_by_category(self, category_id: int) -> int:
        """카테고리별 상품 개수 조회"""
        ...
    
    async def count_all(self) -> int:
        """전체 상품 개수 조회"""
        ...


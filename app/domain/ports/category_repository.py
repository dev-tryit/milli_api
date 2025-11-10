"""CategoryRepository Port (Interface) - Protocol"""

from typing import Protocol
from app.domain.entities.category import Category


class CategoryRepository(Protocol):
    """카테고리 Repository 인터페이스 (Port)"""
    
    async def find_all(self) -> list[Category]:
        """전체 카테고리 조회"""
        ...
    
    async def find_by_id(self, category_id: int) -> Category | None:
        """카테고리 ID로 조회"""
        ...


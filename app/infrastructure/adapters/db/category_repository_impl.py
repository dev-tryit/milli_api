"""CategoryRepository 구현체 (Outbound Adapter)"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.category import Category
from app.domain.ports.category_repository import CategoryRepository
from app.infrastructure.models.category_model import CategoryModel
from app.infrastructure.mappers.category_mapper import CategoryMapper


class CategoryRepositoryImpl:
    """CategoryRepository 구현체 - Outbound Adapter"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = CategoryMapper()
    
    async def find_all(self) -> list[Category]:
        """전체 카테고리 조회"""
        stmt = select(CategoryModel).order_by(CategoryModel.id)
        result = await self.session.execute(stmt)
        category_models = result.scalars().all()
        
        return [self.mapper.to_domain(model) for model in category_models]
    
    async def find_by_id(self, category_id: int) -> Category | None:
        """카테고리 ID로 조회"""
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(stmt)
        category_model = result.scalar_one_or_none()
        
        if not category_model:
            return None
        
        return self.mapper.to_domain(category_model)


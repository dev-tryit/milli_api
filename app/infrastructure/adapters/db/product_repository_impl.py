"""ProductRepository 구현체 (Outbound Adapter)"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domain.entities.product import Product
from app.domain.ports.product_repository import ProductRepository
from app.infrastructure.models.product_model import ProductModel
from app.infrastructure.mappers.product_mapper import ProductMapper


class ProductRepositoryImpl:
    """ProductRepository 구현체 - Outbound Adapter"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = ProductMapper()
    
    async def find_by_id(self, product_id: int) -> Product | None:
        """상품 ID로 조회"""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.session.execute(stmt)
        product_model = result.scalar_one_or_none()
        
        if not product_model:
            return None
        
        return self.mapper.to_domain(product_model)
    
    async def find_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """카테고리별 상품 조회 (OFFSET 기반 페이지네이션)"""
        stmt = (
            select(ProductModel)
            .where(ProductModel.category_id == category_id)
            .order_by(ProductModel.id)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        product_models = result.scalars().all()
        
        return [self.mapper.to_domain(model) for model in product_models]
    
    async def find_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """전체 상품 조회 (OFFSET 기반 페이지네이션)"""
        stmt = (
            select(ProductModel)
            .order_by(ProductModel.id)
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        product_models = result.scalars().all()
        
        return [self.mapper.to_domain(model) for model in product_models]
    
    async def count_by_category(self, category_id: int) -> int:
        """카테고리별 상품 개수 조회"""
        stmt = select(func.count(ProductModel.id)).where(
            ProductModel.category_id == category_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def count_all(self) -> int:
        """전체 상품 개수 조회"""
        stmt = select(func.count(ProductModel.id))
        result = await self.session.execute(stmt)
        return result.scalar_one()


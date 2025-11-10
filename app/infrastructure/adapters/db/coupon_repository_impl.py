"""CouponRepository 구현체 (Outbound Adapter)"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.entities.coupon import Coupon
from app.domain.ports.coupon_repository import CouponRepository
from app.infrastructure.models.coupon_model import CouponModel
from app.infrastructure.mappers.coupon_mapper import CouponMapper


class CouponRepositoryImpl:
    """CouponRepository 구현체 - Outbound Adapter"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = CouponMapper()
    
    async def find_by_code(self, coupon_code: str) -> Coupon | None:
        """쿠폰 코드로 조회"""
        stmt = select(CouponModel).where(CouponModel.code == coupon_code)
        result = await self.session.execute(stmt)
        coupon_model = result.scalar_one_or_none()
        
        if not coupon_model:
            return None
        
        return self.mapper.to_domain(coupon_model)


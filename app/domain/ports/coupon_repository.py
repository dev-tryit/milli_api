"""CouponRepository Port (Interface) - Protocol"""

from typing import Protocol
from app.domain.entities.coupon import Coupon


class CouponRepository(Protocol):
    """쿠폰 Repository 인터페이스 (Port)"""
    
    async def find_by_code(self, coupon_code: str) -> Coupon | None:
        """쿠폰 코드로 조회"""
        ...


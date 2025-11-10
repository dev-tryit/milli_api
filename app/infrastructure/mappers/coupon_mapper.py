"""Coupon Mapper - Domain Model ↔ Infrastructure Model 변환"""

from app.domain.entities.coupon import Coupon
from app.infrastructure.models.coupon_model import CouponModel


class CouponMapper:
    """Coupon Domain Model ↔ Infrastructure Model 변환"""
    
    @staticmethod
    def to_domain(coupon_model: CouponModel) -> Coupon:
        """Infrastructure Model → Domain Model 변환"""
        return Coupon(
            id=coupon_model.id,
            code=coupon_model.code,
            discount_type=coupon_model.discount_type,
            discount_value=coupon_model.discount_value,
            valid_from=coupon_model.valid_from,
            valid_to=coupon_model.valid_to,
        )
    
    @staticmethod
    def to_model(coupon: Coupon, coupon_model: CouponModel | None = None) -> CouponModel:
        """Domain Model → Infrastructure Model 변환"""
        if coupon_model is None:
            coupon_model = CouponModel()
        
        coupon_model.id = coupon.id
        coupon_model.code = coupon.code
        coupon_model.discount_type = coupon.discount_type
        coupon_model.discount_value = coupon.discount_value
        coupon_model.valid_from = coupon.valid_from
        coupon_model.valid_to = coupon.valid_to
        
        return coupon_model


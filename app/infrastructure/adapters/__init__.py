"""Outbound Adapters (Repository 구현체)"""

from app.infrastructure.adapters.db.product_repository_impl import ProductRepositoryImpl
from app.infrastructure.adapters.db.category_repository_impl import CategoryRepositoryImpl
from app.infrastructure.adapters.db.coupon_repository_impl import CouponRepositoryImpl

__all__ = [
    "ProductRepositoryImpl",
    "CategoryRepositoryImpl",
    "CouponRepositoryImpl",
]


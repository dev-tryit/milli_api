"""Repository Ports (Interfaces)"""

from app.domain.ports.product_repository import ProductRepository
from app.domain.ports.category_repository import CategoryRepository
from app.domain.ports.coupon_repository import CouponRepository
from app.domain.ports.cache_adapter import CacheAdapter

__all__ = [
    "ProductRepository",
    "CategoryRepository",
    "CouponRepository",
    "CacheAdapter",
]


"""Product API Mapper - Domain Entity ↔ API Schema 변환"""

from typing import TYPE_CHECKING
from app.application.schemas.product import ProductResponse, ProductDetailResponse

if TYPE_CHECKING:
    from app.domain.entities.product import Product
    from app.domain.entities.coupon import Coupon


class ProductApiMapper:
    """Product Domain Entity ↔ API Schema 변환"""
    
    @staticmethod
    def to_response(product: "Product") -> ProductResponse:
        """Domain Entity → ProductResponse 변환"""
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            stock=product.stock,
            category_id=product.category_id,
            discount_rate=product.discount_rate,
        )
    
    @staticmethod
    def to_detail_response(
        product: "Product",
        coupon: "Coupon | None",
        discounted_price: int,
        final_price: int,
        coupon_discount: int,
    ) -> ProductDetailResponse:
        """Domain Entity → ProductDetailResponse 변환 (상세용)"""
        return ProductDetailResponse(
            id=product.id,
            name=product.name,
            original_price=product.price,
            discount_rate=product.discount_rate,
            discounted_price=discounted_price,
            coupon_code=coupon.code if coupon else None,
            coupon_discount=coupon_discount,
            final_price=final_price,
        )


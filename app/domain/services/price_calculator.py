"""PriceCalculator Domain Service - 복잡한 가격 계산 로직"""

from app.domain.entities.product import Product
from app.domain.entities.coupon import Coupon


class PriceCalculator:
    """가격 계산 도메인 서비스 - 여러 Entity 협력이 필요한 복잡한 로직"""
    
    @staticmethod
    def calculate_with_multiple_coupons(
        product: Product,
        coupons: list[Coupon],
    ) -> int:
        """
        여러 쿠폰을 적용한 최종 가격 계산 (예: 중복 할인 정책)
        
        현재는 단일 쿠폰만 지원하지만, 향후 확장 가능한 구조
        
        Args:
            product: 상품
            coupons: 적용할 쿠폰 목록
            
        Returns:
            최종 판매가
        """
        # 현재는 첫 번째 쿠폰만 적용
        coupon = coupons[0] if coupons else None
        return product.calculate_final_price(coupon)
    
    @staticmethod
    def calculate_bulk_discount(
        product: Product,
        quantity: int,
        bulk_discount_rate: float = 0.0,
    ) -> int:
        """
        대량 구매 할인 계산
        
        Args:
            product: 상품
            quantity: 구매 수량
            bulk_discount_rate: 대량 구매 할인율
            
        Returns:
            수량별 최종 가격
        """
        base_price = product.calculate_final_price()
        bulk_price = int(base_price * (1.0 - bulk_discount_rate))
        return bulk_price * quantity


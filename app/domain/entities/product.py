"""Product Domain Entity - Rich Domain Model"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.entities.coupon import Coupon


class Product:
    """상품 도메인 엔티티 - 비즈니스 로직 포함 (ORM 의존 없음, 순수 Python 클래스)"""
    
    def __init__(
        self,
        id: int,
        name: str,
        price: int,
        stock: int,
        category_id: int,
        discount_rate: float = 0.0,
    ):
        """
        Args:
            id: 상품 ID
            name: 상품명
            price: 원가
            stock: 재고 수량
            category_id: 카테고리 ID
            discount_rate: 할인율 (0.0 ~ 1.0, 예: 0.2 = 20% 할인)
        """
        if price < 0:
            raise ValueError("가격은 0 이상이어야 합니다")
        if stock < 0:
            raise ValueError("재고는 0 이상이어야 합니다")
        if not (0.0 <= discount_rate <= 1.0):
            raise ValueError("할인율은 0.0 ~ 1.0 사이여야 합니다")
        
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category_id = category_id
        self.discount_rate = discount_rate
    
    def calculate_final_price(self, coupon: "Coupon | None" = None) -> int:
        """
        할인율과 쿠폰을 적용한 최종 판매가 계산
        
        계산 순서:
        1. 원가에 할인율 적용
        2. 쿠폰 할인 적용
        
        Args:
            coupon: 적용할 쿠폰 (선택적)
            
        Returns:
            최종 판매가 (정수)
        """
        # 1. 할인율 적용
        discounted_price = self.get_discounted_price()
        
        # 2. 쿠폰 할인 적용
        if coupon:
            if coupon.discount_type == "rate":
                # 비율 할인
                final_price = int(discounted_price * (1.0 - coupon.discount_value))
            elif coupon.discount_type == "amount":
                # 금액 할인
                final_price = max(0, discounted_price - int(coupon.discount_value))
            else:
                raise ValueError(f"알 수 없는 쿠폰 할인 유형: {coupon.discount_type}")
        else:
            final_price = discounted_price
        
        return final_price
    
    def get_discounted_price(self) -> int:
        """할인율만 적용한 가격 (쿠폰 미적용)"""
        return int(self.price * (1.0 - self.discount_rate))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id
    
    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name}, price={self.price}, discount_rate={self.discount_rate})"


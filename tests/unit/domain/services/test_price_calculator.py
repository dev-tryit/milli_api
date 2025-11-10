"""PriceCalculator Domain Service 테스트"""

from app.domain.entities.product import Product
from app.domain.entities.coupon import Coupon
from app.domain.services.price_calculator import PriceCalculator


def test_calculate_with_multiple_coupons():
    """여러 쿠폰 적용 테스트 (현재는 첫 번째 쿠폰만 적용)"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,
    )
    
    coupon1 = Coupon(
        id=1,
        code="SAVE102024AB",
        discount_type="rate",
        discount_value=0.1,
    )
    
    coupon2 = Coupon(
        id=2,
        code="SAVE202024AB",
        discount_type="rate",
        discount_value=0.2,
    )
    
    final_price = PriceCalculator.calculate_with_multiple_coupons(
        product=product,
        coupons=[coupon1, coupon2],
    )
    
    # 첫 번째 쿠폰만 적용: 1000000 * 0.8 * 0.9 = 720000
    assert final_price == 720000


def test_calculate_bulk_discount():
    """대량 구매 할인 계산 테스트"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인 -> 800000
    )
    
    quantity = 5
    bulk_discount_rate = 0.1  # 10% 추가 할인
    
    total_price = PriceCalculator.calculate_bulk_discount(
        product=product,
        quantity=quantity,
        bulk_discount_rate=bulk_discount_rate,
    )
    
    # 800000 * 0.9 * 5 = 3600000
    assert total_price == 3600000


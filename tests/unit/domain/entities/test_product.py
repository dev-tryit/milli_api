"""Product Domain Entity 테스트 (비즈니스 로직 중심)"""

import pytest
from app.domain.entities.product import Product
from app.domain.entities.coupon import Coupon
from app.domain.exceptions import InvalidCouponException


def test_product_creation():
    """상품 생성 테스트"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,
    )
    
    assert product.id == 1
    assert product.name == "노트북"
    assert product.price == 1000000
    assert product.stock == 10
    assert product.category_id == 1
    assert product.discount_rate == 0.2


def test_product_invalid_price():
    """잘못된 가격으로 상품 생성 시 예외 발생"""
    with pytest.raises(ValueError, match="가격은 0 이상이어야 합니다"):
        Product(
            id=1,
            name="노트북",
            price=-1000,
            stock=10,
            category_id=1,
        )


def test_product_invalid_discount_rate():
    """잘못된 할인율로 상품 생성 시 예외 발생"""
    with pytest.raises(ValueError, match="할인율은 0.0 ~ 1.0 사이여야 합니다"):
        Product(
            id=1,
            name="노트북",
            price=1000000,
            stock=10,
            category_id=1,
            discount_rate=1.5,
        )


def test_product_invalid_stock():
    """잘못된 재고로 상품 생성 시 예외 발생"""
    with pytest.raises(ValueError, match="재고는 0 이상이어야 합니다"):
        Product(
            id=1,
            name="노트북",
            price=1000000,
            stock=-10,
            category_id=1,
        )


def test_product_calculate_final_price_without_coupon():
    """쿠폰 없이 최종 가격 계산"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인
    )
    
    final_price = product.calculate_final_price()
    assert final_price == 800000  # 1000000 * 0.8


def test_product_calculate_final_price_with_rate_coupon():
    """비율 할인 쿠폰 적용한 최종 가격 계산"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인
    )
    
    coupon = Coupon(
        id=1,
        code="SAVE102024AB",
        discount_type="rate",
        discount_value=0.1,  # 10% 추가 할인
    )
    
    final_price = product.calculate_final_price(coupon)
    # 1000000 * 0.8 (할인율) * 0.9 (쿠폰) = 720000
    assert final_price == 720000


def test_product_calculate_final_price_with_amount_coupon():
    """금액 할인 쿠폰 적용한 최종 가격 계산"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인 -> 800000
    )
    
    coupon = Coupon(
        id=1,
        code="SAVE50000COD",
        discount_type="amount",
        discount_value=50000,  # 50000원 할인
    )
    
    final_price = product.calculate_final_price(coupon)
    # 800000 - 50000 = 750000
    assert final_price == 750000


def test_product_calculate_final_price_with_amount_coupon_exceeds_price():
    """금액 할인 쿠폰이 가격을 초과하는 경우 (0원 처리)"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인 -> 800000
    )
    
    coupon = Coupon(
        id=1,
        code="SAVE1000000C",
        discount_type="amount",
        discount_value=1000000,  # 1000000원 할인 (가격 초과)
    )
    
    final_price = product.calculate_final_price(coupon)
    # 800000 - 1000000 = 0 (음수 방지)
    assert final_price == 0


def test_product_get_discounted_price():
    """할인율만 적용한 가격 조회"""
    product = Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,  # 20% 할인
    )
    
    discounted_price = product.get_discounted_price()
    assert discounted_price == 800000


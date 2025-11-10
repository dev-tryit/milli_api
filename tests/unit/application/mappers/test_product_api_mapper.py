"""Product API Mapper 테스트"""

import pytest
from app.application.mappers import ProductApiMapper
from app.domain.entities.product import Product
from app.domain.entities.coupon import Coupon
from datetime import datetime, timedelta


@pytest.fixture
def sample_product():
    """샘플 상품"""
    return Product(
        id=1,
        name="노트북",
        price=1000000,
        stock=10,
        category_id=1,
        discount_rate=0.2,
    )


@pytest.fixture
def sample_coupon():
    """샘플 쿠폰"""
    now = datetime.now()
    return Coupon(
        id=1,
        code="SAVE102024AB",
        discount_type="rate",
        discount_value=0.1,
        valid_from=now - timedelta(days=1),
        valid_to=now + timedelta(days=1),
    )


def test_to_response(sample_product):
    """Domain Entity → ProductResponse 변환 테스트"""
    mapper = ProductApiMapper()
    response = mapper.to_response(sample_product)
    
    assert response.id == 1
    assert response.name == "노트북"
    assert response.price == 1000000
    assert response.stock == 10
    assert response.category_id == 1
    assert response.discount_rate == 0.2


def test_to_detail_response_without_coupon(sample_product):
    """Domain Entity → ProductDetailResponse 변환 테스트 (쿠폰 없음)"""
    mapper = ProductApiMapper()
    
    discounted_price = sample_product.get_discounted_price()
    final_price = sample_product.calculate_final_price(None)
    coupon_discount = 0
    
    response = mapper.to_detail_response(
        product=sample_product,
        coupon=None,
        discounted_price=discounted_price,
        final_price=final_price,
        coupon_discount=coupon_discount,
    )
    
    assert response.id == 1
    assert response.name == "노트북"
    assert response.original_price == 1000000
    assert response.discount_rate == 0.2
    assert response.discounted_price == 800000  # 20% 할인
    assert response.coupon_code is None
    assert response.coupon_discount == 0
    assert response.final_price == 800000


def test_to_detail_response_with_coupon(sample_product, sample_coupon):
    """Domain Entity → ProductDetailResponse 변환 테스트 (쿠폰 적용)"""
    mapper = ProductApiMapper()
    
    discounted_price = sample_product.get_discounted_price()
    final_price = sample_product.calculate_final_price(sample_coupon)
    coupon_discount = discounted_price - final_price
    
    response = mapper.to_detail_response(
        product=sample_product,
        coupon=sample_coupon,
        discounted_price=discounted_price,
        final_price=final_price,
        coupon_discount=coupon_discount,
    )
    
    assert response.id == 1
    assert response.name == "노트북"
    assert response.original_price == 1000000
    assert response.discount_rate == 0.2
    assert response.discounted_price == 800000  # 20% 할인
    assert response.coupon_code == "SAVE102024AB"
    assert response.coupon_discount == 80000  # 10% 추가 할인
    assert response.final_price == 720000  # 최종 가격


"""Coupon Domain Entity 테스트"""

import pytest
from datetime import datetime, timedelta
from app.domain.entities.coupon import Coupon


def test_coupon_creation():
    """쿠폰 생성 테스트"""
    coupon = Coupon(
        id=1,
        code="SAVE102024AB",
        discount_type="rate",
        discount_value=0.1,
    )
    
    assert coupon.id == 1
    assert coupon.code == "SAVE102024AB"
    assert coupon.discount_type == "rate"
    assert coupon.discount_value == 0.1


def test_coupon_invalid_discount_type():
    """잘못된 할인 유형으로 쿠폰 생성 시 예외 발생"""
    # 쿠폰 코드는 유효하지만 할인 유형이 잘못됨
    with pytest.raises(ValueError, match="할인 유형은 'rate' 또는 'amount'여야 합니다"):
        Coupon(
            id=1,
            code="INVALIDTYPE1",
            discount_type="invalid",
            discount_value=0.1,
        )


def test_coupon_invalid_rate_value():
    """잘못된 비율 할인 값으로 쿠폰 생성 시 예외 발생"""
    # 쿠폰 코드는 유효하지만 할인 값이 잘못됨
    with pytest.raises(ValueError, match="비율 할인은 0.0 ~ 1.0 사이여야 합니다"):
        Coupon(
            id=1,
            code="INVALIDRATE1",
            discount_type="rate",
            discount_value=1.5,
        )


def test_coupon_invalid_code_format():
    """잘못된 쿠폰 코드 형식으로 쿠폰 생성 시 예외 발생"""
    # 쿠폰 코드가 12자리가 아니거나 형식이 맞지 않음
    with pytest.raises(ValueError, match="쿠폰 코드는 12자리의 대문자 알파벳과 숫자만 허용됩니다"):
        Coupon(
            id=1,
            code="INVALID",  # 12자리가 아님
            discount_type="rate",
            discount_value=0.1,
        )
    
    # 소문자 포함
    with pytest.raises(ValueError, match="쿠폰 코드는 12자리의 대문자 알파벳과 숫자만 허용됩니다"):
        Coupon(
            id=1,
            code="invalidcode12",  # 소문자 포함
            discount_type="rate",
            discount_value=0.1,
        )
    
    # 특수문자 포함
    with pytest.raises(ValueError, match="쿠폰 코드는 12자리의 대문자 알파벳과 숫자만 허용됩니다"):
        Coupon(
            id=1,
            code="INVALID-CODE1",  # 특수문자 포함
            discount_type="rate",
            discount_value=0.1,
        )


def test_coupon_invalid_amount_value():
    """잘못된 금액 할인 값으로 쿠폰 생성 시 예외 발생"""
    with pytest.raises(ValueError, match="금액 할인은 0 이상이어야 합니다"):
        Coupon(
            id=1,
            code="INVALIDAMT12",  # 유효한 12자리 코드
            discount_type="amount",
            discount_value=-1000,  # 음수 금액
        )


def test_coupon_is_valid():
    """쿠폰 유효성 검증 테스트"""
    now = datetime.now()
    coupon = Coupon(
        id=1,
        code="VALIDCODE202",
        discount_type="rate",
        discount_value=0.1,
        valid_from=now - timedelta(days=1),
        valid_to=now + timedelta(days=1),
    )
    
    assert coupon.is_valid(now=now) is True


def test_coupon_is_invalid_before_valid_from():
    """유효 시작일 이전 쿠폰은 유효하지 않음"""
    now = datetime.now()
    coupon = Coupon(
        id=1,
            code="INVALIDCODE1",
        discount_type="rate",
        discount_value=0.1,
        valid_from=now + timedelta(days=1),
        valid_to=now + timedelta(days=2),
    )
    
    assert coupon.is_valid(now=now) is False


def test_coupon_is_invalid_after_valid_to():
    """유효 종료일 이후 쿠폰은 유효하지 않음"""
    now = datetime.now()
    coupon = Coupon(
        id=1,
            code="INVALIDCODE1",
        discount_type="rate",
        discount_value=0.1,
        valid_from=now - timedelta(days=2),
        valid_to=now - timedelta(days=1),
    )
    
    assert coupon.is_valid(now=now) is False


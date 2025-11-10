"""ProductService Application Service 테스트 (비즈니스 로직 중심)"""

import pytest
from unittest.mock import AsyncMock
from app.application.services.product_service import ProductService
from app.domain.entities.product import Product
from app.domain.entities.coupon import Coupon
from app.domain.exceptions import (
    ProductNotFoundException,
    CouponNotFoundException,
    InvalidCouponException,
)
from app.domain.ports.cache_adapter import CacheAdapter
from datetime import datetime, timedelta


@pytest.fixture
def mock_product_repository():
    """Mock ProductRepository"""
    return AsyncMock()


@pytest.fixture
def mock_coupon_repository():
    """Mock CouponRepository"""
    return AsyncMock()


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


@pytest.mark.asyncio
async def test_get_product_list_with_category(
    mock_product_repository,
    sample_product,
    mock_cache_adapter,
):
    """카테고리별 상품 목록 조회 테스트"""
    mock_product_repository.find_by_category = AsyncMock(return_value=[sample_product])
    mock_cache_adapter.get_product_list = AsyncMock(return_value=None)
    mock_cache_adapter.set_product_list = AsyncMock()
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    products = await service.get_product_list(category_id=1, offset=0, limit=20)
    
    assert len(products) == 1
    assert products[0].id == 1
    mock_product_repository.find_by_category.assert_called_once_with(
        category_id=1,
        offset=0,
        limit=20,
    )


@pytest.mark.asyncio
async def test_get_product_list_without_category(
    mock_product_repository,
    sample_product,
    mock_cache_adapter,
):
    """전체 상품 목록 조회 테스트"""
    mock_product_repository.find_all = AsyncMock(return_value=[sample_product])
    mock_cache_adapter.get_product_list = AsyncMock(return_value=None)
    mock_cache_adapter.set_product_list = AsyncMock()
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    products = await service.get_product_list(offset=0, limit=20)
    
    assert len(products) == 1
    mock_product_repository.find_all.assert_called_once_with(
        offset=0,
        limit=20,
    )


@pytest.mark.asyncio
async def test_get_product_detail_success(
    mock_product_repository,
    mock_coupon_repository,
    sample_product,
    mock_cache_adapter,
):
    """상품 상세 조회 성공 테스트 (쿠폰 없음)"""
    mock_product_repository.find_by_id = AsyncMock(return_value=sample_product)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=mock_coupon_repository,
        cache_adapter=mock_cache_adapter,
    )
    
    product, coupon = await service.get_product_detail(product_id=1)
    
    assert product.id == 1
    assert coupon is None
    mock_product_repository.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_product_detail_with_coupon(
    mock_product_repository,
    mock_coupon_repository,
    sample_product,
    sample_coupon,
    mock_cache_adapter,
):
    """상품 상세 조회 성공 테스트 (쿠폰 적용)"""
    mock_product_repository.find_by_id = AsyncMock(return_value=sample_product)
    mock_coupon_repository.find_by_code = AsyncMock(return_value=sample_coupon)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=mock_coupon_repository,
        cache_adapter=mock_cache_adapter,
    )
    
    product, coupon = await service.get_product_detail(
        product_id=1,
        coupon_code="SAVE102024AB",
    )
    
    assert product.id == 1
    assert coupon is not None
    assert coupon.code == "SAVE102024AB"
    mock_product_repository.find_by_id.assert_called_once_with(1)
    mock_coupon_repository.find_by_code.assert_called_once_with("SAVE102024AB")


@pytest.mark.asyncio
async def test_get_product_detail_product_not_found(
    mock_product_repository,
    mock_cache_adapter,
):
    """상품을 찾을 수 없을 때 예외 발생"""
    mock_product_repository.find_by_id = AsyncMock(return_value=None)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    with pytest.raises(ProductNotFoundException) as exc_info:
        await service.get_product_detail(product_id=999)
    
    assert exc_info.value.product_id == 999


@pytest.mark.asyncio
async def test_get_product_detail_coupon_not_found(
    mock_product_repository,
    mock_coupon_repository,
    sample_product,
    mock_cache_adapter,
):
    """쿠폰을 찾을 수 없을 때 예외 발생"""
    mock_product_repository.find_by_id = AsyncMock(return_value=sample_product)
    mock_coupon_repository.find_by_code = AsyncMock(return_value=None)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=mock_coupon_repository,
        cache_adapter=mock_cache_adapter,
    )
    
    with pytest.raises(CouponNotFoundException) as exc_info:
        await service.get_product_detail(product_id=1, coupon_code="INVALIDCODE12")
    
    assert exc_info.value.coupon_code == "INVALIDCODE12"


@pytest.mark.asyncio
async def test_get_product_detail_invalid_coupon(
    mock_product_repository,
    mock_coupon_repository,
    sample_product,
    mock_cache_adapter,
):
    """쿠폰이 유효하지 않을 때 예외 발생"""
    now = datetime.now()
    expired_coupon = Coupon(
        id=1,
        code="EXPIREDCODE1",
        discount_type="rate",
        discount_value=0.1,
        valid_from=now - timedelta(days=2),
        valid_to=now - timedelta(days=1),  # 만료됨
    )
    
    mock_product_repository.find_by_id = AsyncMock(return_value=sample_product)
    mock_coupon_repository.find_by_code = AsyncMock(return_value=expired_coupon)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=mock_coupon_repository,
        cache_adapter=mock_cache_adapter,
    )
    
    with pytest.raises(InvalidCouponException) as exc_info:
        await service.get_product_detail(product_id=1, coupon_code="EXPIREDCODE12")
    
    assert exc_info.value.coupon_code == "EXPIREDCODE12"


@pytest.fixture
def mock_cache_adapter():
    """Mock CacheAdapter"""
    return AsyncMock(spec=CacheAdapter)


@pytest.mark.asyncio
async def test_get_product_list_cache_hit(
    mock_product_repository,
    sample_product,
    mock_cache_adapter,
):
    """Redis 캐시 히트 시나리오 테스트"""
    # 캐시에서 데이터 반환
    mock_cache_adapter.get_product_list = AsyncMock(return_value=[sample_product])
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    products = await service.get_product_list(category_id=1, offset=0, limit=20)
    
    assert len(products) == 1
    assert products[0].id == 1
    # 캐시에서 조회했으므로 DB는 호출되지 않음
    mock_product_repository.find_by_category.assert_not_called()
    mock_cache_adapter.get_product_list.assert_called_once_with(
        category_id=1,
        offset=0,
        limit=20,
    )


@pytest.mark.asyncio
async def test_get_product_list_cache_miss(
    mock_product_repository,
    sample_product,
    mock_cache_adapter,
):
    """Redis 캐시 미스 시나리오 테스트"""
    # 캐시에서 데이터 없음
    mock_cache_adapter.get_product_list = AsyncMock(return_value=None)
    mock_cache_adapter.set_product_list = AsyncMock()
    mock_product_repository.find_by_category = AsyncMock(return_value=[sample_product])
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    products = await service.get_product_list(category_id=1, offset=0, limit=20)
    
    assert len(products) == 1
    # 캐시 미스 후 DB 조회
    mock_product_repository.find_by_category.assert_called_once_with(
        category_id=1,
        offset=0,
        limit=20,
    )
    # 캐시에 저장
    mock_cache_adapter.set_product_list.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_list_redis_failure_fallback(
    mock_product_repository,
    sample_product,
    mock_cache_adapter,
):
    """Redis 연결 실패 시 DB로 fallback 테스트"""
    # Redis 예외 발생
    mock_cache_adapter.get_product_list = AsyncMock(side_effect=Exception("Redis connection failed"))
    mock_product_repository.find_by_category = AsyncMock(return_value=[sample_product])
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    products = await service.get_product_list(category_id=1, offset=0, limit=20)
    
    # Redis 실패해도 DB로 fallback하여 정상 동작
    assert len(products) == 1
    mock_product_repository.find_by_category.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_count_cache_hit(
    mock_product_repository,
    mock_cache_adapter,
):
    """상품 개수 조회 캐시 히트 테스트"""
    mock_cache_adapter.get_product_count = AsyncMock(return_value=100)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    count = await service.get_product_count(category_id=1)
    
    assert count == 100
    # 캐시에서 조회했으므로 DB는 호출되지 않음
    mock_product_repository.count_by_category.assert_not_called()


@pytest.mark.asyncio
async def test_get_product_count_cache_miss(
    mock_product_repository,
    mock_cache_adapter,
):
    """상품 개수 조회 캐시 미스 테스트"""
    mock_cache_adapter.get_product_count = AsyncMock(return_value=None)
    mock_cache_adapter.set_product_count = AsyncMock()
    mock_product_repository.count_by_category = AsyncMock(return_value=50)
    
    service = ProductService(
        product_repository=mock_product_repository,
        coupon_repository=None,
        cache_adapter=mock_cache_adapter,
    )
    
    count = await service.get_product_count(category_id=1)
    
    assert count == 50
    # 캐시 미스 후 DB 조회
    mock_product_repository.count_by_category.assert_called_once_with(1)
    # 캐시에 저장
    mock_cache_adapter.set_product_count.assert_called_once()


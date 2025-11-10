"""CRUD 통합 테스트 - 데이터베이스 CRUD 작업 검증"""

import pytest
from datetime import datetime, timedelta
from tests.integration.helpers.db_helpers import (
    with_db_session,
    create_test_category,
    cleanup_test_category,
    create_test_product,
    cleanup_test_product,
    create_test_coupon,
    cleanup_test_coupon,
)
from app.infrastructure.adapters.db.category_repository_impl import CategoryRepositoryImpl
from app.infrastructure.adapters.db.product_repository_impl import ProductRepositoryImpl
from app.infrastructure.adapters.db.coupon_repository_impl import CouponRepositoryImpl


@pytest.mark.asyncio
async def test_category_crud():
    """카테고리 CRUD 테스트"""
    # 테스트 데이터 생성
    await create_test_category()
    
    try:
        async with with_db_session() as session:
            repository = CategoryRepositoryImpl(session)
            
            # Read: 카테고리 조회
            category = await repository.find_by_id(999)
            assert category is not None
            assert category.id == 999
            assert category.name == "테스트 카테고리"
            
            # Read: 전체 카테고리 조회
            categories = await repository.find_all()
            assert len(categories) > 0
            assert any(c.id == 999 for c in categories)
    finally:
        # 정리
        await cleanup_test_category()


@pytest.mark.asyncio
async def test_product_crud():
    """상품 CRUD 테스트"""
    # 테스트 데이터 생성
    await create_test_category()
    
    try:
        # Create: 상품 생성
        await create_test_product(
            product_id=999,
            name="테스트 상품",
            price=10000,
            stock=100,
            category_id=999,
            discount_rate=0.1,
        )
        
        try:
            # Read: 상품 조회 테스트
            async with with_db_session() as session:
                repository = ProductRepositoryImpl(session)
                
                # Read: 상품 ID로 조회
                product = await repository.find_by_id(999)
                assert product is not None
                assert product.id == 999
                assert product.name == "테스트 상품"
                assert product.price == 10000
                assert product.stock == 100
                assert product.category_id == 999
                assert product.discount_rate == 0.1
                
                # Read: 카테고리별 상품 조회
                products = await repository.find_by_category(
                    category_id=999,
                    offset=0,
                    limit=10
                )
                assert len(products) > 0
                assert any(p.id == 999 for p in products)
                
                # Read: 전체 상품 조회
                all_products = await repository.find_all(offset=0, limit=10)
                assert len(all_products) > 0
                assert any(p.id == 999 for p in all_products)
                
                # Read: 카테고리별 개수 조회
                count = await repository.count_by_category(999)
                assert count > 0
                
                # Read: 전체 개수 조회
                total_count = await repository.count_all()
                assert total_count > 0
        finally:
            # Delete: 테스트 데이터 정리
            await cleanup_test_product(999)
    finally:
        # 카테고리 정리
        await cleanup_test_category()


@pytest.mark.asyncio
async def test_coupon_crud():
    """쿠폰 CRUD 테스트"""
    # Create: 쿠폰 생성
    now = datetime.now()
    valid_from = now - timedelta(days=1)
    valid_to = now + timedelta(days=1)
    
    await create_test_coupon(
        coupon_id=999,
        code="TESTCOUPON12",
        discount_type="rate",
        discount_value=0.1,
        valid_from=valid_from,
        valid_to=valid_to,
    )
    
    try:
        async with with_db_session() as session:
            repository = CouponRepositoryImpl(session)
            
            # Read: 쿠폰 코드로 조회
            coupon = await repository.find_by_code("TESTCOUPON12")
            assert coupon is not None
            assert coupon.id == 999
            assert coupon.code == "TESTCOUPON12"
            assert coupon.discount_type == "rate"
            assert coupon.discount_value == 0.1
            assert coupon.valid_from is not None
            assert coupon.valid_to is not None
    finally:
        # Delete: 테스트 데이터 정리
        await cleanup_test_coupon(999)


@pytest.mark.asyncio
async def test_product_with_coupon_calculation():
    """상품과 쿠폰을 함께 사용한 가격 계산 테스트"""
    # 테스트 데이터 생성
    await create_test_category()
    
    now = datetime.now()
    valid_from = now - timedelta(days=1)
    valid_to = now + timedelta(days=1)
    
    try:
        # Create: 상품 및 쿠폰 생성
        await create_test_product(
            product_id=998,
            name="할인 상품",
            price=10000,
            stock=50,
            category_id=999,
            discount_rate=0.2,
        )
                
        await create_test_coupon(
            coupon_id=998,
            code="TESTCOUPON98",
            discount_type="rate",
            discount_value=0.1,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        
        try:
            # Read: 상품과 쿠폰 조회 및 가격 계산
            async with with_db_session() as session:
                product_repo = ProductRepositoryImpl(session)
                coupon_repo = CouponRepositoryImpl(session)
                
                # 상품 조회
                product = await product_repo.find_by_id(998)
                assert product is not None
                
                # 쿠폰 조회
                coupon = await coupon_repo.find_by_code("TESTCOUPON98")
                assert coupon is not None
                
                # 가격 계산 검증
                # 원가: 10000
                # 할인율 20% 적용: 8000
                # 쿠폰 10% 적용: 7200
                discounted_price = product.get_discounted_price()
                assert discounted_price == 8000
                
                final_price = product.calculate_final_price(coupon)
                assert final_price == 7200
        finally:
            # 정리
            await cleanup_test_product(998)
            await cleanup_test_coupon(998)
    finally:
        # 카테고리 정리
        await cleanup_test_category()

"""Product API 통합 테스트 - API 엔드포인트, validation, 에러 핸들링 검증"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.application.main import app


@pytest.fixture(scope="function")
async def client():
    """FastAPI TestClient fixture"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_get_product_list_success(client: AsyncClient):
    """상품 목록 조회 API - 응답 구조 검증"""
    response = await client.get("/api/products?limit=10&page=1")
    
    assert response.status_code == 200
    data = response.json()
    
    # 응답 스키마 검증
    assert "products" in data
    assert isinstance(data["products"], list)
    assert "total_count" in data
    assert "total_pages" in data
    assert "current_page" in data
    assert "limit" in data
    
    # 페이지네이션 값 검증
    assert data["current_page"] == 1
    assert data["limit"] == 10
    assert data["total_count"] >= 0
    assert data["total_pages"] >= 0


@pytest.mark.asyncio
async def test_get_product_list_with_category_filter(client: AsyncClient):
    """상품 목록 조회 API - 카테고리 필터링 파라미터 검증"""
    response = await client.get("/api/products?category_id=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)


@pytest.mark.asyncio
async def test_get_product_list_validation_error(client: AsyncClient):
    """상품 목록 조회 API - 잘못된 파라미터 validation 검증"""
    # limit이 100을 초과하는 경우
    response = await client.get("/api/products?limit=101")
    assert response.status_code == 422
    
    # page가 0 이하인 경우
    response = await client.get("/api/products?page=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_product_detail_not_found(client: AsyncClient):
    """상품 상세 조회 API - 상품 없음 404 에러 핸들링 검증"""
    response = await client.get("/api/products/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "찾을 수 없습니다" in data["detail"]


@pytest.mark.asyncio
async def test_get_product_detail_invalid_id(client: AsyncClient):
    """상품 상세 조회 API - 잘못된 product_id validation 검증"""
    # product_id가 0 이하인 경우
    response = await client.get("/api/products/0")
    assert response.status_code == 422
    
    # product_id가 정수가 아닌 경우
    response = await client.get("/api/products/invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_product_detail_with_invalid_coupon_format(client: AsyncClient):
    """상품 상세 조회 API - 잘못된 쿠폰 코드 형식 validation 검증"""
    # 쿠폰 코드가 12자리가 아닌 경우
    response = await client.get("/api/products/1?coupon_code=SHORT")
    assert response.status_code == 422
    
    # 쿠폰 코드에 소문자가 포함된 경우
    response = await client.get("/api/products/1?coupon_code=save102024ab")
    assert response.status_code == 422
    
    # 쿠폰 코드에 특수문자가 포함된 경우
    response = await client.get("/api/products/1?coupon_code=SAVE-2024-AB")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_product_detail_with_valid_coupon_format(client: AsyncClient):
    """상품 상세 조회 API - 유효한 쿠폰 코드 형식 파라미터 검증"""
    # 유효한 쿠폰 코드 형식 (12자리 대문자+숫자)
    # 상품이 없거나 쿠폰이 없어도 404는 정상 (validation은 통과)
    response = await client.get("/api/products/1?coupon_code=SAVE102024AB")
    
    # validation 통과 후 비즈니스 로직에서 404 발생 가능
    assert response.status_code in [404, 400]
    
    # 404인 경우: 상품 또는 쿠폰 없음
    # 400인 경우: 쿠폰 유효하지 않음 (만료 등)
    if response.status_code == 404:
        data = response.json()
        assert "detail" in data


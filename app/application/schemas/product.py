"""Product API Schemas (Pydantic)"""

from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class ProductListRequest(BaseModel):
    """상품 목록 조회 요청"""
    model_config = ConfigDict(json_schema_extra={"examples": [{"category_id": 1, "page": 1, "limit": 20}]})
    
    category_id: Annotated[int | None, Field(description="카테고리 ID", ge=1)] = None
    page: Annotated[int, Field(description="페이지 번호 (1부터 시작)", ge=1)] = 1
    limit: Annotated[int, Field(description="조회 개수", ge=1, le=100)] = 20


class ProductResponse(BaseModel):
    """상품 응답"""
    model_config = ConfigDict(json_schema_extra={"examples": [{"id": 1, "name": "노트북", "price": 1000000, "stock": 10, "category_id": 1, "discount_rate": 0.2}]})
    
    id: Annotated[int, Field(description="상품 ID", ge=1)]
    name: Annotated[str, Field(description="상품명", min_length=1)]
    price: Annotated[int, Field(description="원가", ge=0)]
    stock: Annotated[int, Field(description="재고 수량", ge=0)]
    category_id: Annotated[int, Field(description="카테고리 ID", ge=1)]
    discount_rate: Annotated[float, Field(description="할인율", ge=0.0, le=1.0)]


class ProductListResponse(BaseModel):
    """상품 목록 응답"""
    products: Annotated[list[ProductResponse], Field(description="상품 목록")]
    total_count: Annotated[int, Field(description="전체 상품 개수", ge=0)]
    total_pages: Annotated[int, Field(description="전체 페이지 수", ge=0)]
    current_page: Annotated[int, Field(description="현재 페이지 번호", ge=1)]
    limit: Annotated[int, Field(description="페이지당 조회 개수", ge=1, le=100)]


class ProductDetailRequest(BaseModel):
    """상품 상세 조회 요청"""
    model_config = ConfigDict(json_schema_extra={"examples": [{"coupon_code": "SAVE102024AB"}]})
    
    coupon_code: Annotated[str | None, Field(description="쿠폰 코드 (12자리, 대문자 알파벳과 숫자만 허용)", min_length=12, max_length=12, pattern="^[A-Z0-9]{12}$")] = None


class ProductDetailResponse(BaseModel):
    """상품 상세 응답"""
    model_config = ConfigDict(json_schema_extra={"examples": [{"id": 1, "name": "노트북", "original_price": 1000000, "discount_rate": 0.2, "discounted_price": 800000, "coupon_code": "SAVE102024AB", "coupon_discount": 80000, "final_price": 720000}]})
    
    id: Annotated[int, Field(description="상품 ID", ge=1)]
    name: Annotated[str, Field(description="상품명", min_length=1)]
    original_price: Annotated[int, Field(description="원가", ge=0)]
    discount_rate: Annotated[float, Field(description="할인율", ge=0.0, le=1.0)]
    discounted_price: Annotated[int, Field(description="할인가 (할인율 적용)", ge=0)]
    coupon_code: Annotated[str | None, Field(description="적용된 쿠폰 코드 (12자리)", min_length=12, max_length=12, pattern="^[A-Z0-9]{12}$")] = None
    coupon_discount: Annotated[int, Field(description="쿠폰 할인 금액", ge=0)] = 0
    final_price: Annotated[int, Field(description="최종 판매가", ge=0)]


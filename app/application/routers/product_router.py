"""Product API Router (Inbound Adapter)"""

from math import ceil

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dependencies import (
    get_cache_adapter,
    get_db_session,
)
from app.infrastructure.adapters.db.coupon_repository_impl import CouponRepositoryImpl
from app.infrastructure.adapters.db.product_repository_impl import ProductRepositoryImpl
from app.application.mappers import ProductApiMapper
from app.application.schemas.product import (
    ProductDetailRequest,
    ProductDetailResponse,
    ProductListRequest,
    ProductListResponse,
)
from app.application.services.product_service import ProductService
from app.domain.exceptions import (
    CouponNotFoundException,
    DomainException,
    InvalidCouponException,
    ProductNotFoundException,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def get_product_list(
    request: ProductListRequest = Depends(),
    session: AsyncSession = Depends(get_db_session),
    cache_adapter=Depends(get_cache_adapter),
):
    """
    상품 목록 조회
    
    - 카테고리별 필터링 지원
    - OFFSET 기반 페이지네이션
    - Redis 캐싱 지원
    """
    product_repository = ProductRepositoryImpl(session)
    service = ProductService(
        product_repository=product_repository,
        coupon_repository=None,  # 목록 조회에는 쿠폰 불필요
        cache_adapter=cache_adapter,
    )
    
    # OFFSET 계산
    offset = (request.page - 1) * request.limit
    
    # 상품 목록 및 개수 조회
    products = await service.get_product_list(
        category_id=request.category_id,
        offset=offset,
        limit=request.limit,
    )
    
    total_count = await service.get_product_count(category_id=request.category_id)
    total_pages = ceil(total_count / request.limit)
    
    # Domain Entity → API Schema 변환 (Mapper 사용)
    mapper = ProductApiMapper()
    
    return ProductListResponse(
        products=[mapper.to_response(p) for p in products],
        total_count=total_count,
        total_pages=total_pages,
        current_page=request.page,
        limit=request.limit,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(
    product_id: int = Path(..., ge=1, description="상품 ID"),
    coupon_code: str | None = Query(None, description="쿠폰 코드 (12자리, 대문자 알파벳과 숫자만 허용)", min_length=12, max_length=12, pattern="^[A-Z0-9]{12}$"),
    session: AsyncSession = Depends(get_db_session),
    cache_adapter=Depends(get_cache_adapter),
):
    """
    상품 상세 조회 및 가격 계산
    
    - 할인율 적용
    - 쿠폰 적용 (선택적)
    - 최종 판매가 계산
    """
    product_repository = ProductRepositoryImpl(session)
    coupon_repository = CouponRepositoryImpl(session)
    service = ProductService(
        product_repository=product_repository,
        coupon_repository=coupon_repository,
        cache_adapter=cache_adapter,
    )
    
    try:
        product, coupon = await service.get_product_detail(
            product_id=product_id,
            coupon_code=coupon_code,
        )
    except ProductNotFoundException as e:
        raise HTTPException(status_code=404, detail="요청하신 상품을 찾을 수 없습니다")
    except CouponNotFoundException as e:
        raise HTTPException(status_code=404, detail="유효하지 않은 쿠폰 코드입니다")
    except InvalidCouponException as e:
        raise HTTPException(status_code=400, detail="사용할 수 없는 쿠폰입니다")
    
    # 가격 계산
    discounted_price = product.get_discounted_price()
    final_price = product.calculate_final_price(coupon)
    coupon_discount = discounted_price - final_price if coupon else 0
    
    # Domain Entity → API Schema 변환 (Mapper 사용)
    mapper = ProductApiMapper()
    return mapper.to_detail_response(
        product=product,
        coupon=coupon,
        discounted_price=discounted_price,
        final_price=final_price,
        coupon_discount=coupon_discount,
    )


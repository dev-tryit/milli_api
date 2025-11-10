"""ProductService - Application Service (Use Case)"""

from datetime import datetime

from app.application.utils.cache_helper import cache_aside
from app.domain.entities.coupon import Coupon
from app.domain.entities.product import Product
from app.domain.exceptions import (
    CouponNotFoundException,
    InvalidCouponException,
    ProductNotFoundException,
)
from app.domain.ports.cache_adapter import CacheAdapter
from app.domain.ports.coupon_repository import CouponRepository
from app.domain.ports.product_repository import ProductRepository


class ProductService:
    """상품 관리 Application Service - Use Case 구현"""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        coupon_repository: CouponRepository | None,
        cache_adapter: CacheAdapter,
    ):
        """
        Args:
            product_repository: 상품 Repository (Port)
            coupon_repository: 쿠폰 Repository (Port, 선택적)
            cache_adapter: 캐시 어댑터 (Port, 필수)
        """
        self.product_repository = product_repository
        self.coupon_repository = coupon_repository
        self.cache_adapter = cache_adapter
    
    async def get_product_list(
        self,
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """
        상품 목록 조회 (Cache-Aside 패턴 적용)
        
        Args:
            category_id: 카테고리 ID (선택적)
            offset: OFFSET 값
            limit: 조회 개수
            
        Returns:
            상품 목록
        """
        async def cache_get() -> list[Product] | None:
            return await self.cache_adapter.get_product_list(
                category_id=category_id,
                offset=offset,
                limit=limit,
            )
        
        async def db_fetch() -> list[Product]:
            # 트랜잭션 관리는 Router/Dependencies에서 처리 (get_db_session)
            if category_id:
                return await self.product_repository.find_by_category(
                    category_id=category_id,
                    offset=offset,
                    limit=limit,
                )
            else:
                return await self.product_repository.find_all(
                    offset=offset,
                    limit=limit,
                )
        
        async def cache_set(products: list[Product]) -> None:
            await self.cache_adapter.set_product_list(
                products=products,
                category_id=category_id,
                offset=offset,
                limit=limit,
            )
        
        return await cache_aside(
            cache_get=cache_get,
            db_fetch=db_fetch,
            cache_set=cache_set,
        )
    
    async def get_product_count(
        self,
        category_id: int | None = None,
    ) -> int:
        """
        상품 개수 조회 (Cache-Aside 패턴 적용)
        
        Args:
            category_id: 카테고리 ID (선택적)
            
        Returns:
            상품 개수
        """
        async def cache_get() -> int | None:
            return await self.cache_adapter.get_product_count(
                category_id=category_id,
            )
        
        async def db_fetch() -> int:
            # 트랜잭션 관리는 Router/Dependencies에서 처리 (get_db_session)
            if category_id:
                return await self.product_repository.count_by_category(category_id)
            else:
                return await self.product_repository.count_all()
        
        async def cache_set(count: int) -> None:
            await self.cache_adapter.set_product_count(
                count=count,
                category_id=category_id,
            )
        
        return await cache_aside(
            cache_get=cache_get,
            db_fetch=db_fetch,
            cache_set=cache_set,
        )
    
    async def get_product_detail(
        self,
        product_id: int,
        coupon_code: str | None = None,
    ) -> tuple[Product, Coupon | None]:
        """
        상품 상세 조회 및 쿠폰 조회
        
        Args:
            product_id: 상품 ID
            coupon_code: 쿠폰 코드 (선택적)
            
        Returns:
            (상품, 쿠폰) 튜플
            
        Raises:
            ProductNotFoundException: 상품을 찾을 수 없을 때
            CouponNotFoundException: 쿠폰을 찾을 수 없을 때
            InvalidCouponException: 쿠폰이 유효하지 않을 때
        """
        # 트랜잭션 관리는 Router/Dependencies에서 처리 (get_db_session)
        # 상품 조회
        product = await self.product_repository.find_by_id(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        
        # 쿠폰 조회 (선택적)
        coupon = None
        if coupon_code:
            if not self.coupon_repository:
                raise CouponNotFoundException(coupon_code)
            
            coupon = await self.coupon_repository.find_by_code(coupon_code)
            if not coupon:
                raise CouponNotFoundException(coupon_code)
            
            # 쿠폰 유효성 검사
            now = datetime.now()
            if coupon.valid_from > now or coupon.valid_to < now:
                raise InvalidCouponException(coupon_code, "쿠폰 유효 기간이 만료되었습니다")
        
        return product, coupon

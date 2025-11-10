"""Redis Cache Adapter (Outbound Adapter)"""

import json
import logging
import redis.asyncio as redis
from app.domain.entities.product import Product

logger = logging.getLogger(__name__)


class RedisCacheAdapter:
    """Redis 캐시 어댑터 - 상품 리스트 캐싱"""
    
    def __init__(self, redis_client: redis.Redis, ttl: int = 300):
        """
        Args:
            redis_client: Redis 클라이언트
            ttl: 캐시 TTL (초 단위, 기본 5분)
        """
        self.redis_client = redis_client
        self.ttl = ttl
    
    async def get_product_list(
        self,
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product] | None:
        """캐시에서 상품 목록 조회"""
        try:
            cache_key = self._build_list_cache_key(category_id, offset, limit)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # JSON 역직렬화 후 Product Entity로 변환
                data_list = json.loads(cached_data)
                products = [
                    Product(
                        id=item["id"],
                        name=item["name"],
                        price=item["price"],
                        stock=item["stock"],
                        category_id=item["category_id"],
                        discount_rate=item["discount_rate"],
                    )
                    for item in data_list
                ]
                return products
            
            return None
        except Exception as e:
            logger.warning(f"Redis 캐시 조회 실패: {e}")
            return None
    
    async def set_product_list(
        self,
        products: list[Product],
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> None:
        """상품 목록을 캐시에 저장"""
        try:
            cache_key = self._build_list_cache_key(category_id, offset, limit)
            # Product Entity를 JSON으로 직렬화
            data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "stock": p.stock,
                    "category_id": p.category_id,
                    "discount_rate": p.discount_rate,
                }
                for p in products
            ]
            await self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(data),
            )
        except Exception as e:
            logger.warning(f"Redis 캐시 저장 실패: {e}")
            # 에러를 발생시키지 않고 조용히 실패 (fallback to DB)
    
    async def get_product_count(
        self,
        category_id: int | None = None,
    ) -> int | None:
        """캐시에서 상품 개수 조회"""
        try:
            cache_key = self._build_count_cache_key(category_id)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return int(cached_data)
            
            return None
        except Exception as e:
            logger.warning(f"Redis 캐시 조회 실패: {e}")
            return None
    
    async def set_product_count(
        self,
        count: int,
        category_id: int | None = None,
    ) -> None:
        """상품 개수를 캐시에 저장"""
        try:
            cache_key = self._build_count_cache_key(category_id)
            await self.redis_client.setex(
                cache_key,
                self.ttl,
                str(count),
            )
        except Exception as e:
            logger.warning(f"Redis 캐시 저장 실패: {e}")
            # 에러를 발생시키지 않고 조용히 실패 (fallback to DB)
    
    def _build_list_cache_key(
        self,
        category_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> str:
        """상품 목록 캐시 키 생성"""
        parts = ["products", "list"]
        if category_id:
            parts.append(f"category:{category_id}")
        parts.append(f"offset:{offset}")
        parts.append(f"limit:{limit}")
        return ":".join(parts)
    
    def _build_count_cache_key(
        self,
        category_id: int | None = None,
    ) -> str:
        """상품 개수 캐시 키 생성"""
        parts = ["products", "count"]
        if category_id:
            parts.append(f"category:{category_id}")
        else:
            parts.append("all")
        return ":".join(parts)


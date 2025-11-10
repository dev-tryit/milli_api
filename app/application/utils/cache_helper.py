"""Cache Helper Utilities - Cache-Aside 패턴 템플릿"""

from typing import Awaitable, Callable, TypeVar

T = TypeVar('T')


async def cache_aside(
    cache_get: Callable[[], Awaitable[T | None]],
    db_fetch: Callable[[], Awaitable[T]],
    cache_set: Callable[[T], Awaitable[None]] | None = None,
) -> T:
    """
    Cache-Aside 패턴 템플릿 함수
    
    캐시를 먼저 조회하고, 캐시 미스 시 DB에서 조회한 후 캐시에 저장하는 패턴을 구현합니다.
    
    Args:
        cache_get: 캐시 조회 함수 (None 반환 시 캐시 미스)
        db_fetch: DB 조회 함수
        cache_set: 캐시 저장 함수 (선택적, None이면 저장하지 않음)
        
    Returns:
        조회된 데이터
        
    Example:
        ```python
        async def cache_get() -> list[Product] | None:
            return await cache_adapter.get_product_list(...)
        
        async def db_fetch() -> list[Product]:
            return await repository.find_all(...)
        
        async def cache_set(products: list[Product]) -> None:
            await cache_adapter.set_product_list(products, ...)
        
        products = await cache_aside(cache_get, db_fetch, cache_set)
        ```
    """
    # 1. 캐시 조회 시도
    try:
        cached_value = await cache_get()
        if cached_value is not None:
            return cached_value
    except Exception:
        # Redis 실패 시 조용히 DB로 fallback
        pass
    
    # 2. 캐시 미스 - DB 조회
    result = await db_fetch()
    
    # 3. 캐시 저장 (비동기, 에러가 발생해도 조용히 실패)
    if cache_set and result:
        try:
            await cache_set(result)
        except Exception:
            pass  # 로깅은 adapter 내부에서 처리
    
    return result


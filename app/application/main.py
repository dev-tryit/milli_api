"""FastAPI Application Main"""

import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from app.application.routers import product_router
from app.domain.exceptions import DomainException
from app.infrastructure.settings.config import settings, engine, async_session_maker
from app.infrastructure.adapters.cache.redis_client import get_redis_client

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shopping Mall API",
    description="RESTful 쇼핑몰 상품 관리 API - 헥사고날 아키텍처 + DDD",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Pydantic ValidationError를 한글 메시지로 변환"""
    errors = exc.errors()
    
    # 한글 에러 메시지 매핑
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        error_type = error["type"]
        msg = error.get("msg", "")
        
        # 에러 타입별 한글 메시지
        if error_type == "greater_than_equal":
            constraint = error.get("ctx", {}).get("ge")
            error_messages.append(f"{field}은(는) {constraint} 이상이어야 합니다")
        elif error_type == "less_than_equal":
            constraint = error.get("ctx", {}).get("le")
            error_messages.append(f"{field}은(는) {constraint} 이하여야 합니다")
        elif error_type == "greater_than":
            constraint = error.get("ctx", {}).get("gt")
            error_messages.append(f"{field}은(는) {constraint}보다 커야 합니다")
        elif error_type == "less_than":
            constraint = error.get("ctx", {}).get("lt")
            error_messages.append(f"{field}은(는) {constraint}보다 작아야 합니다")
        elif error_type == "value_error.missing":
            error_messages.append(f"{field}은(는) 필수 입력 항목입니다")
        elif error_type == "type_error.integer":
            error_messages.append(f"{field}은(는) 정수여야 합니다")
        elif error_type == "type_error.str":
            error_messages.append(f"{field}은(는) 문자열이어야 합니다")
        else:
            # 기본 메시지
            error_messages.append(f"{field}: {msg}")
    
    response_content = {
        "detail": error_messages,
    }
    
    # 개발 환경에서만 원본 에러 정보 포함
    if settings.debug or settings.environment == "development":
        response_content["errors"] = errors
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content,
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """
    모든 예외를 잡는 안전망 (최후의 방어선)
    
    처리되지 않은 모든 예외를 500으로 처리
    - DomainException: Router에서 명시적으로 처리하지 못한 도메인 예외 (개발자 실수)
    - 기타 예외: 예상치 못한 모든 예외
    
    단, HTTPException과 RequestValidationError는 FastAPI가 자동으로 처리하므로 제외
    """
    # HTTPException은 FastAPI가 자동으로 처리하므로 다시 raise
    if isinstance(exc, HTTPException):
        raise exc
    
    # RequestValidationError도 이미 처리했으므로 제외
    if isinstance(exc, RequestValidationError):
        raise exc
    
    # DomainException 또는 기타 예외 모두 500으로 처리
    response_content = {
        "detail": "서버 내부 오류가 발생했습니다",
    }
    
    # 개발 환경에서만 상세 에러 메시지 포함
    if settings.debug or settings.environment == "development":
        error_message = exc.message if isinstance(exc, DomainException) else str(exc)
        response_content["error"] = error_message
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content,
    )


# 라우터 등록
app.include_router(product_router.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 및 Redis 연결 확인"""
    logger.info("서버 시작 중...")
    
    # 데이터베이스 연결 확인
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✓ 데이터베이스 연결 성공")
    except Exception as e:
        logger.error("✗ 데이터베이스 연결 실패: %s", e)
        logger.error("데이터베이스가 실행 중인지 확인하세요: make docker-up")
        raise
    
    # Redis 연결 확인
    try:
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            logger.info("✓ Redis 연결 성공")
        else:
            logger.warning("⚠ Redis가 비활성화되어 있습니다")
    except Exception as e:
        logger.warning("⚠ Redis 연결 실패: %s. 캐시 없이 동작합니다.", e)
    
    logger.info("서버 시작 완료")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 리소스 정리"""
    logger.info("서버 종료 중...")
    from app.infrastructure.adapters.cache.redis_client import close_redis_client
    await close_redis_client()
    await engine.dispose()
    logger.info("서버 종료 완료")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Shopping Mall API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """헬스 체크 - 데이터베이스 및 Redis 연결 상태 확인"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
    }
    
    # 데이터베이스 연결 확인
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"disconnected: {str(e)}"
    
    # Redis 연결 확인
    try:
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disabled"
    except Exception as e:
        health_status["redis"] = f"disconnected: {str(e)}"
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content=health_status,
    )


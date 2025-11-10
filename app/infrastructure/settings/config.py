"""Database Configuration"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://user:password@localhost:3306/shopping_mall"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"  # 개발 환경 여부
    environment: str = os.getenv("ENVIRONMENT", "development")  # 환경 (development, production)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_enabled: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))  # 캐시 TTL (초 단위, 기본 5분)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

# AsyncEngine 생성
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=False,  # SQL 로그 출력 여부
    pool_pre_ping=True,  # 연결 유효성 검사
    pool_recycle=3600,  # 1시간마다 연결 재사용
)

# AsyncSessionMaker 생성
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy Base 클래스 - 모든 ORM 모델의 부모"""
    pass


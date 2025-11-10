"""Alembic Environment Configuration"""

import os
import logging
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
from app.infrastructure.settings.config import Base, settings
from app.infrastructure.models import ProductModel, CategoryModel, CouponModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

logger = logging.getLogger("alembic.env")


def get_url():
    """
    데이터베이스 URL 가져오기
    
    우선순위:
    1. 환경변수 DATABASE_URL
    2. alembic.ini의 sqlalchemy.url (비어있으면 무시)
    3. settings.database_url (기본값)
    
    Docker 환경에서는 환경변수나 docker-compose.yml의 설정을 사용
    """
    # 환경변수 우선 사용
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info("Using DATABASE_URL from environment variable")
        return database_url
    
    # alembic.ini에서 설정된 URL 확인
    alembic_url = config.get_main_option("sqlalchemy.url")
    if alembic_url and alembic_url.strip():
        logger.info("Using sqlalchemy.url from alembic.ini")
        return alembic_url
    
    # 기본값: settings에서 가져오기
    logger.info("Using database_url from settings")
    return settings.database_url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    logger.info(f"Running migrations in offline mode with URL: {url.split('@')[-1] if '@' in url else url}")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 타입 변경 감지
        compare_server_default=True,  # 기본값 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """실제 마이그레이션 실행"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 컬럼 타입 변경 감지
        compare_server_default=True,  # 기본값 변경 감지
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    database_url = get_url()
    logger.info(f"Running migrations in online mode with URL: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 마이그레이션 시에는 풀 사용 안 함
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    logger.info("Running migrations in OFFLINE mode")
    run_migrations_offline()
else:
    logger.info("Running migrations in ONLINE mode")
    run_migrations_online()


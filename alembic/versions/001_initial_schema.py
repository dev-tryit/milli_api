"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Categories 테이블
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Products 테이블
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('discount_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_products_category_id')
    )
    
    # Coupons 테이블
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('discount_type', sa.String(length=20), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('valid_from', sa.DateTime(), nullable=True),
        sa.Column('valid_to', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 인덱스 생성 (02번 답변 참고 - 커버링 인덱스)
    # products(category_id, id) - 카테고리 필터링 + 커서 기반 페이지네이션
    op.create_index(
        'idx_products_category_id',
        'products',
        ['category_id', 'id'],
        unique=False
    )
    
    # coupons.code 인덱스 (쿠폰 코드 조회 최적화)
    op.create_index(
        'idx_coupons_code',
        'coupons',
        ['code'],
        unique=True
    )


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('idx_coupons_code', table_name='coupons')
    op.drop_index('idx_products_category_id', table_name='products')
    
    # 테이블 삭제
    op.drop_table('coupons')
    op.drop_table('products')
    op.drop_table('categories')


"""Product ORM Model (Infrastructure Model)"""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.settings.config import Base


class ProductModel(Base):
    """상품 ORM 모델 - 데이터베이스 매핑만 담당"""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[int]
    stock: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    discount_rate: Mapped[float] = mapped_column(default=0.0, server_default="0.0")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, server_default=sa.func.now())
    
    # 인덱스: 카테고리 필터링 + 커서 기반 페이지네이션 최적화
    __table_args__ = (
        Index("idx_products_category_id", "category_id", "id"),
    )


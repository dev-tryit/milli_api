"""Coupon ORM Model (Infrastructure Model)"""

from datetime import datetime

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.settings.config import Base


class CouponModel(Base):
    """쿠폰 ORM 모델 - 데이터베이스 매핑만 담당"""
    
    __tablename__ = "coupons"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50))
    discount_type: Mapped[str] = mapped_column(String(20))  # "rate" or "amount"
    discount_value: Mapped[float]
    valid_from: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    
    # 인덱스: 쿠폰 코드 조회 최적화 (마이그레이션과 일치)
    __table_args__ = (
        Index("idx_coupons_code", "code", unique=True),
    )


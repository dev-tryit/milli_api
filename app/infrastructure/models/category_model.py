"""Category ORM Model (Infrastructure Model)"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.settings.config import Base


class CategoryModel(Base):
    """카테고리 ORM 모델 - 데이터베이스 매핑만 담당"""
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


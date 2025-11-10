"""Category Mapper - Domain Model ↔ Infrastructure Model 변환"""

from app.domain.entities.category import Category
from app.infrastructure.models.category_model import CategoryModel


class CategoryMapper:
    """Category Domain Model ↔ Infrastructure Model 변환"""
    
    @staticmethod
    def to_domain(category_model: CategoryModel) -> Category:
        """Infrastructure Model → Domain Model 변환"""
        return Category(
            id=category_model.id,
            name=category_model.name,
        )
    
    @staticmethod
    def to_model(category: Category, category_model: CategoryModel | None = None) -> CategoryModel:
        """Domain Model → Infrastructure Model 변환"""
        if category_model is None:
            category_model = CategoryModel()
        
        category_model.id = category.id
        category_model.name = category.name
        
        return category_model


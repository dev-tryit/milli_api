"""Product Mapper - Domain Model ↔ Infrastructure Model 변환"""

from app.domain.entities.product import Product
from app.infrastructure.models.product_model import ProductModel


class ProductMapper:
    """Product Domain Model ↔ Infrastructure Model 변환"""
    
    @staticmethod
    def to_domain(product_model: ProductModel) -> Product:
        """Infrastructure Model → Domain Model 변환"""
        return Product(
            id=product_model.id,
            name=product_model.name,
            price=product_model.price,
            stock=product_model.stock,
            category_id=product_model.category_id,
            discount_rate=product_model.discount_rate,
        )
    
    @staticmethod
    def to_model(product: Product, product_model: ProductModel | None = None) -> ProductModel:
        """Domain Model → Infrastructure Model 변환"""
        if product_model is None:
            product_model = ProductModel()
        
        product_model.id = product.id
        product_model.name = product.name
        product_model.price = product.price
        product_model.stock = product.stock
        product_model.category_id = product.category_id
        product_model.discount_rate = product.discount_rate
        
        return product_model


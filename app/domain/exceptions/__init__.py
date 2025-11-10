"""Domain Exceptions - 비즈니스 예외 정의"""


class DomainException(Exception):
    """도메인 예외 기본 클래스 - 비즈니스 예외 (복구 가능)"""
    status_code: int = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ProductNotFoundException(DomainException):
    """상품을 찾을 수 없을 때 발생하는 예외"""
    
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"상품 {product_id}를 찾을 수 없습니다")


class CategoryNotFoundException(DomainException):
    """카테고리를 찾을 수 없을 때 발생하는 예외"""
    
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"카테고리 {category_id}를 찾을 수 없습니다")


class CouponNotFoundException(DomainException):
    """쿠폰을 찾을 수 없을 때 발생하는 예외"""
    
    def __init__(self, coupon_code: str):
        self.coupon_code = coupon_code
        super().__init__(f"쿠폰 코드 '{coupon_code}'를 찾을 수 없습니다")


class InvalidCouponException(DomainException):
    """쿠폰이 유효하지 않을 때 발생하는 예외 (만료, 사용 불가 등)"""
    
    def __init__(self, coupon_code: str, reason: str):
        self.coupon_code = coupon_code
        self.reason = reason
        super().__init__(f"쿠폰 코드 '{coupon_code}'가 유효하지 않습니다: {reason}")


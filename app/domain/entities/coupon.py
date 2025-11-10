"""Coupon Domain Entity"""

import re
from datetime import datetime


class Coupon:
    """쿠폰 도메인 엔티티"""
    
    def __init__(
        self,
        id: int,
        code: str,
        discount_type: str,
        discount_value: float,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
    ):
        """
        Args:
            id: 쿠폰 ID
            code: 쿠폰 코드 (12자리, 대문자 알파벳과 숫자만 허용)
            discount_type: 할인 유형 ("rate" 또는 "amount")
            discount_value: 할인 값 (rate: 0.0~1.0, amount: 할인 금액)
            valid_from: 유효 시작일 (선택적)
            valid_to: 유효 종료일 (선택적)
        """
        # 쿠폰 코드 유효성 검사: 정확히 12자리, 대문자 알파벳과 숫자만 허용
        if not re.match(r"^[A-Z0-9]{12}$", code):
            raise ValueError("쿠폰 코드는 12자리의 대문자 알파벳과 숫자만 허용됩니다")
        
        if discount_type not in ("rate", "amount"):
            raise ValueError("할인 유형은 'rate' 또는 'amount'여야 합니다")
        if discount_type == "rate" and not (0.0 <= discount_value <= 1.0):
            raise ValueError("비율 할인은 0.0 ~ 1.0 사이여야 합니다")
        if discount_type == "amount" and discount_value < 0:
            raise ValueError("금액 할인은 0 이상이어야 합니다")
        
        self.id = id
        self.code = code
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.valid_from = valid_from
        self.valid_to = valid_to
    
    def is_valid(self, now: datetime | None = None) -> bool:
        """쿠폰이 유효한지 확인"""
        if now is None:
            now = datetime.now()
        
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        
        return True
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coupon):
            return False
        return self.id == other.id
    
    def __repr__(self) -> str:
        return f"Coupon(id={self.id}, code={self.code}, type={self.discount_type}, value={self.discount_value})"


"""Category Domain Entity"""


class Category:
    """카테고리 도메인 엔티티"""
    
    def __init__(self, id: int, name: str):
        if not name or not name.strip():
            raise ValueError("카테고리명은 필수입니다")
        
        self.id = id
        self.name = name.strip()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Category):
            return False
        return self.id == other.id
    
    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name})"


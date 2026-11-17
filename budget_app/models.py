from dataclasses import dataclass, field
from typing import List

@dataclass
class Transaction:
    """거래 내역 데이터 모델"""
    id: str
    type: str  # 'income' 또는 'expense'
    date: str  # 'YYYY-MM-DD'
    amount: int
    category: str
    memo: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class Category:
    """카테고리 데이터 모델"""
    name: str

@dataclass
class Budget:
    """월별 예산 데이터 모델"""
    month: str  # 'YYYY-MM'
    amount: int
from dataclasses import dataclass, field
from typing import List

@dataclass
class Transaction:
    id: str
    type: str  # 'income' or 'expense'
    date: str  # YYYY-MM-DD
    amount: int
    category: str
    memo: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "memo": self.memo,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            id=data["id"],
            type=data["type"],
            date=data["date"],
            amount=int(data["amount"]),
            category=data["category"],
            memo=data.get("memo", ""),
            tags=tags
        )

@dataclass
class Category:
    name: str
from dataclasses import dataclass, field
from typing import Any


#  개별 수입 및 지출 거래 데이터 구조 및 정의
@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)
    recurring_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id, "type": self.type, "date": self.date,
            "amount": self.amount, "category": self.category,
            "memo": self.memo, "tags": self.tags,
        }
        if self.recurring_key is not None:
            result["recurring_key"] = self.recurring_key
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Transaction":
        if not isinstance(data, dict):
            raise ValueError("거래 데이터가 JSON 객체가 아닙니다.")
        tags = data.get("tags", [])
        if isinstance(tags, str):  # 이전 버전 데이터와 호환
            tags = [s.strip() for s in tags.split(",") if s.strip()]
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError("tags는 문자열 배열이어야 합니다.")
        amount = data["amount"]
        if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
            raise ValueError("amount는 양의 정수여야 합니다.")
        for key in ("id", "type", "date", "category"):
            if not isinstance(data[key], str):
                raise ValueError(f"{key}는 문자열이어야 합니다.")
        if data["type"] not in ("income", "expense"):
            raise ValueError("거래 타입이 올바르지 않습니다.")
        from .validation import validate_date
        validate_date(data["date"])
        memo = data.get("memo", "")
        recurring_key = data.get("recurring_key")
        if not isinstance(memo, str) or (recurring_key is not None and not isinstance(recurring_key, str)):
            raise ValueError("메모 또는 반복 거래 키의 형식이 잘못되었습니다.")
        return cls(
            id=data["id"], type=data["type"], date=data["date"],
            amount=amount, category=data["category"], memo=memo,
            tags=tags, recurring_key=recurring_key,
        )


# 카페고리 이름 데이터 구조 및 정의
@dataclass
class Category:
    name: str


#  매월 반복되는 거래 데이터 구조 및 정의 [보너스 - 2]
@dataclass
class RecurringRule:
    id: str
    type: str
    category: str
    amount: int
    day: int
    start_month: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecurringRule":
        if not isinstance(data, dict):
            raise ValueError("반복 규칙 데이터가 JSON 객체가 아닙니다.")
        rule = cls(**data)
        if not isinstance(rule.id, str) or not rule.id:
            raise ValueError("반복 규칙 ID가 잘못되었습니다.")
        if rule.type not in ("income", "expense"):
            raise ValueError("반복 규칙 타입이 잘못되었습니다.")
        if not isinstance(rule.category, str) or not rule.category:
            raise ValueError("반복 규칙 카테고리가 잘못되었습니다.")
        if type(rule.amount) is not int or rule.amount <= 0:
            raise ValueError("반복 규칙 금액이 잘못되었습니다.")
        if type(rule.day) is not int or not 1 <= rule.day <= 31:
            raise ValueError("반복 규칙 일자가 잘못되었습니다.")
        from .validation import validate_month
        validate_month(rule.start_month)
        if not isinstance(rule.memo, str) or not isinstance(rule.tags, list) or not all(isinstance(t, str) for t in rule.tags):
            raise ValueError("반복 규칙 메모/태그 형식이 잘못되었습니다.")
        return rule

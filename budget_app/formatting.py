import unicodedata
from typing import Iterable
from .models import Transaction


COLUMNS = [("ID", 35), ("날짜", 10), ("유형", 7), ("카테고리", 14),
           ("금액", 13), ("메모", 20), ("태그", 18)]


def _display_width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in value)


def _cell(value: object, width: int, right: bool = False) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ").replace("\t", " ")
    if _display_width(text) > width:
        shortened = ""
        for char in text:
            if _display_width(shortened + char) > width - 1:
                break
            shortened += char
        text = shortened + "…"
    padding = " " * (width - _display_width(text))
    return padding + text if right else text + padding


def print_transactions(transactions: Iterable[Transaction]) -> int:
    headings = " | ".join(_cell(name, width) for name, width in COLUMNS)
    print(headings)
    print("-" * len(headings))
    count = 0
    for tx in transactions:
        values = [tx.id, tx.date, tx.type, tx.category,
                  f"{tx.amount:,}원", tx.memo, ",".join(tx.tags)]
        print(" | ".join(
            _cell(value, width, right=(index == 4))
            for index, ((name, width), value) in enumerate(zip(COLUMNS, values))
        ))
        count += 1
    if count == 0:
        print("데이터 없음")
    print(f"조회 건수: {count}")
    return count

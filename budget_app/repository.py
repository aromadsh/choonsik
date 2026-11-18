import json
import os
import shutil
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Iterator

from .models import Category, RecurringRule, Transaction
from .validation import validate_month


DEFAULT_CATEGORIES = ["food", "transport", "rent", "salary", "entertainment", "other"]


class StorageRepository:
    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trans_file = self.data_dir / "transactions.jsonl"
        self.cat_file = self.data_dir / "categories.jsonl"
        self.budget_file = self.data_dir / "budgets.jsonl"
        self.recurring_file = self.data_dir / "recurring.jsonl"
        self._init_files()

    def _init_files(self) -> None:
        if not self.cat_file.exists():
            self.save_categories([Category(name=c) for c in DEFAULT_CATEGORIES])
        for path in (self.trans_file, self.budget_file, self.recurring_file):
            path.touch(exist_ok=True)

    @staticmethod
    def _read_jsonl(path: Path) -> Iterator[dict]:
        with path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError("JSON 객체가 아닙니다.")
                    yield record
                except (ValueError, TypeError) as error:
                    raise ValueError(f"{path.name} {line_number}행이 손상되었습니다: {error}") from error

    def _atomic_write(self, path: Path, lines: Iterable[str]) -> None:
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n",
                dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
                delete=False,
            ) as temp:
                temp_name = temp.name
                for line in lines:
                    temp.write(line + "\n")
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(temp_name, path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _append_jsonl(path: Path, records: Iterable[dict]) -> int:
        count = 0
        with path.open("a", encoding="utf-8", newline="\n") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            file.flush()
            os.fsync(file.fileno())
        return count

    def stream_transactions(self) -> Iterator[Transaction]:
        with self.trans_file.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    yield Transaction.from_dict(record)
                except (ValueError, TypeError, KeyError) as error:
                    raise ValueError(
                        f"transactions.jsonl {line_number}행이 잘못되었습니다: {error}"
                    ) from error

    def get_all_transactions(self) -> list[Transaction]:
        return list(self.stream_transactions())

    def add_transaction(self, tx: Transaction) -> None:
        self._append_jsonl(self.trans_file, (tx.to_dict() for _ in range(1)))

    def add_transactions(self, transactions: Iterable[Transaction]) -> int:
        return self._append_jsonl(self.trans_file, (tx.to_dict() for tx in transactions))

    def save_all_transactions(self, transactions: Iterable[Transaction]) -> None:
        self._atomic_write(self.trans_file, (
            json.dumps(t.to_dict(), ensure_ascii=False) for t in transactions
        ))

    def edit_transaction(self, tx_id: str, change: Callable[[Transaction], Transaction | None]) -> bool:
        found = False

        def updated_lines() -> Iterator[str]:
            nonlocal found
            for tx in self.stream_transactions():
                if tx.id == tx_id:
                    found = True
                    result = change(tx)
                    if result is not None:
                        yield json.dumps(result.to_dict(), ensure_ascii=False)
                else:
                    yield json.dumps(tx.to_dict(), ensure_ascii=False)

        # 존재하지 않는 ID라도 원본 손상 여부 검증 후 동일 데이터로 재작성됨
        self._atomic_write(self.trans_file, updated_lines())
        return found

    def get_categories(self) -> list[str]:
        categories: list[str] = []
        for data in self._read_jsonl(self.cat_file):
            name = data.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("카테고리 파일에 올바르지 않은 이름이 있습니다.")
            categories.append(name)
        return categories

    def save_categories(self, categories: list[Category]) -> None:
        self._atomic_write(self.cat_file, (
            json.dumps({"name": c.name}, ensure_ascii=False) for c in categories
        ))

    def add_category(self, name: str) -> bool:
        categories = self.get_categories()
        if name in categories:
            return False
        categories.append(name)
        self.save_categories([Category(name=c) for c in categories])
        return True

    def remove_category(self, name: str) -> bool:
        categories = self.get_categories()
        if name not in categories:
            return False
        categories.remove(name)
        self.save_categories([Category(name=c) for c in categories])
        return True

    def get_budgets(self) -> dict[str, int]:
        budgets: dict[str, int] = {}
        for data in self._read_jsonl(self.budget_file):
            month = validate_month(data.get("month"))
            amount = data.get("amount")
            if type(amount) is not int or amount < 0:
                raise ValueError("예산 데이터의 금액이 잘못되었습니다.")
            budgets[month] = amount
        return budgets

    def set_budget(self, month: str, amount: int) -> None:
        budgets = self.get_budgets()
        budgets[month] = amount
        self._atomic_write(self.budget_file, (
            json.dumps({"month": m, "amount": a}, ensure_ascii=False)
            for m, a in sorted(budgets.items())
        ))

    def get_budget(self, month: str) -> int | None:
        return self.get_budgets().get(month)

    def stream_recurring(self) -> Iterator[RecurringRule]:
        for data in self._read_jsonl(self.recurring_file):
            try:
                yield RecurringRule.from_dict(data)
            except (TypeError, ValueError) as error:
                raise ValueError(f"반복 규칙 파일이 잘못되었습니다: {error}") from error

    def add_recurring(self, rule: RecurringRule) -> None:
        self._append_jsonl(self.recurring_file, (asdict(rule),))

    def backup(self) -> str:
        # 초 단위 중복 시에도 새 폴더를 생성함
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(tempfile.mkdtemp(prefix=f"backup_{stamp}_", dir=self.data_dir))
        for path in (self.trans_file, self.cat_file, self.budget_file, self.recurring_file):
            shutil.copy2(path, backup_dir / path.name)
        return str(backup_dir)

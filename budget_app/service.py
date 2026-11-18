import calendar
import csv
import heapq
import json
import os
import tempfile
import uuid
from dataclasses import asdict, replace
from pathlib import Path
from typing import Iterable, Iterator

from .models import RecurringRule, Transaction
from .repository import StorageRepository
from .validation import positive_amount, positive_count, validate_date, validate_month, validate_period


CSV_COLUMNS = ["date", "type", "category", "amount", "memo", "tags"]


def _date_order(tx: Transaction) -> tuple[str, str]:
    return (tx.date, tx.id)


def _file_transactions(path: Path) -> Iterator[Transaction]:
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            yield Transaction.from_dict(json.loads(line))


def sort_transactions(source: Iterable[Transaction], chunk_size: int = 500) -> Iterator[Transaction]:
    """큰 검색 결과도 임시 JSONL 청크로 외부 정렬하여 메모리 사용 제한."""
    with tempfile.TemporaryDirectory(prefix="budget_sort_") as folder:
        files: list[Path] = []
        chunk: list[Transaction] = []

        def save_chunk() -> None:
            chunk.sort(key=_date_order, reverse=True)
            path = Path(folder) / f"chunk_{len(files)}.jsonl"
            with path.open("w", encoding="utf-8") as file:
                for tx in chunk:
                    file.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")
            files.append(path)
            chunk.clear()

        for tx in source:
            chunk.append(tx)
            if len(chunk) >= chunk_size:
                save_chunk()
        if not files:
            yield from sorted(chunk, key=_date_order, reverse=True)
            return
        if chunk:
            save_chunk()
        yield from heapq.merge(
            *(_file_transactions(path) for path in files),
            key=_date_order, reverse=True,
        )


class BudgetService:
    def __init__(self, data_dir: str = "./data") -> None:
        self.repo = StorageRepository(data_dir)

    def _validated_fields(
        self, date: str, type_val: str, category: str, amount: int,
    ) -> None:
        validate_date(date)
        if type_val not in ("income", "expense"):
            raise ValueError("타입은 income 또는 expense여야 합니다.")
        if category not in self.repo.get_categories():
            raise ValueError(f"등록되지 않은 카테고리입니다: {category}. category list로 확인하세요.")
        positive_amount(amount)

    def generate_id(self) -> str:
        return "TX-" + uuid.uuid4().hex

    def add_transaction(
        self, date: str, type_val: str, category: str, amount: int,
        memo: str = "", tags: list[str] | None = None,
    ) -> str:
        self._validated_fields(date, type_val, category, amount)
        tx = Transaction(
            id=self.generate_id(), type=type_val, date=date,
            amount=amount, category=category, memo=memo,
            tags=tags or [],
        )
        self.repo.add_transaction(tx)
        return tx.id

    def list_transactions(self, limit: int = 10) -> list[Transaction]:
        positive_count(limit, "--limit")
        return heapq.nlargest(limit, self.repo.stream_transactions(), key=_date_order)

    def search_transactions(
        self, from_date: str | None = None, to_date: str | None = None,
        category: str | None = None, type_val: str | None = None,
        q: str | None = None, tag: str | None = None,
    ) -> Iterator[Transaction]:
        validate_period(from_date, to_date)
        if type_val is not None and type_val not in ("income", "expense"):
            raise ValueError("--type은 income 또는 expense여야 합니다.")
        if category is not None and category not in self.repo.get_categories():
            raise ValueError(f"등록되지 않은 카테고리입니다: {category}")

        def matching() -> Iterator[Transaction]:
            for tx in self.repo.stream_transactions():
                if from_date and tx.date < from_date:
                    continue
                if to_date and tx.date > to_date:
                    continue
                if category and tx.category != category:
                    continue
                if type_val and tx.type != type_val:
                    continue
                if q and q.casefold() not in tx.memo.casefold():
                    continue
                if tag and tag not in tx.tags:
                    continue
                yield tx

        return sort_transactions(matching())

    def update_transaction(
        self, tx_id: str, date: str | None = None, type_val: str | None = None,
        category: str | None = None, amount: int | None = None,
        memo: str | None = None, tags: list[str] | None = None,
    ) -> bool:
        if date is not None:
            validate_date(date)
        if type_val is not None and type_val not in ("income", "expense"):
            raise ValueError("타입은 income 또는 expense여야 합니다.")
        if category is not None and category not in self.repo.get_categories():
            raise ValueError(f"등록되지 않은 카테고리입니다: {category}")
        if amount is not None:
            positive_amount(amount)

        def change(tx: Transaction) -> Transaction:
            values = {}
            for name, value in (
                ("date", date), ("type", type_val), ("category", category),
                ("amount", amount), ("memo", memo), ("tags", tags),
            ):
                if value is not None:
                    values[name] = value
            return replace(tx, **values)

        return self.repo.edit_transaction(tx_id, change)

    def delete_transaction(self, tx_id: str) -> bool:
        return self.repo.edit_transaction(tx_id, lambda tx: None)

    def summary(self, month: str, top_n: int = 3) -> None:
        validate_month(month)
        positive_count(top_n, "--top")
        income = expense = count = 0
        expenses: dict[str, int] = {}
        for tx in self.repo.stream_transactions():
            if tx.date[:7] != month:
                continue
            count += 1
            if tx.type == "income":
                income += tx.amount
            else:
                expense += tx.amount
                expenses[tx.category] = expenses.get(tx.category, 0) + tx.amount
        if not count:
            print(f"[데이터 없음] {month}에 등록된 거래가 없습니다.")
        print(f"총 수입: {income}원")
        print(f"총 지출: {expense}원")
        print(f"잔액: {income - expense}원")
        budget = self.repo.get_budget(month)
        if budget is None:
            print("예산: 미설정")
        elif budget == 0:
            print("예산: 0원 (사용률: 계산 불가 — 예산 0원)")
            if expense > 0:
                print("[경고] 예산을 초과했습니다!")
        else:
            print(f"예산: {budget}원 (사용률 {expense / budget * 100:.1f}%)")
            if expense > budget:
                print("[경고] 예산을 초과했습니다!")
        print(f"\n지출 TOP {top_n}")
        for index, (category, amount) in enumerate(
            sorted(expenses.items(), key=lambda item: (-item[1], item[0]))[:top_n], 1,
        ):
            print(f"{index}) {category} {amount}원")
        if not expenses:
            print("지출 데이터 없음")

    def set_budget(self, month: str, amount: int) -> None:
        validate_month(month)
        if type(amount) is not int or amount < 0:
            raise ValueError("예산 금액은 0 이상의 정수여야 합니다.")
        self.repo.set_budget(month, amount)

    def manage_category(self, action: str, name: str | None = None) -> None:
        if action == "list":
            print("등록된 카테고리:")
            categories = self.repo.get_categories()
            for category in categories:
                print(f"- {category}")
            if not categories:
                print("등록된 카테고리가 없습니다.")
            return
        if not name or not name.strip():
            raise ValueError("카테고리 이름을 입력해야 합니다.")
        name = name.strip()
        if action == "add":
            if not self.repo.add_category(name):
                raise ValueError(f"이미 등록된 카테고리입니다: {name}")
            print(f"[저장 완료] category={name}")
        elif action == "remove":
            if any(tx.category == name for tx in self.repo.stream_transactions()):
                raise ValueError(f"카테고리 {name}을 사용하는 거래가 있어 삭제할 수 없습니다.")
            if any(rule.category == name for rule in self.repo.stream_recurring()):
                raise ValueError(f"카테고리 {name}을 사용하는 반복 규칙이 있어 삭제할 수 없습니다.")
            if not self.repo.remove_category(name):
                raise ValueError(f"존재하지 않는 카테고리입니다: {name}")
            print(f"[삭제 완료] category={name}")
        else:
            raise ValueError("지원하지 않는 category 명령어입니다.")

    def export_csv(
        self, out_path: str, month: str | None = None,
        from_date: str | None = None, to_date: str | None = None,
    ) -> int:
        if month is None and from_date is None and to_date is None:
            raise ValueError("export는 --month 또는 --from/--to 조건이 필요합니다.")
        if month is not None:
            validate_month(month)
        validate_period(from_date, to_date)
        destination = Path(out_path).resolve()
        protected = {p.resolve() for p in (
            self.repo.trans_file, self.repo.cat_file,
            self.repo.budget_file, self.repo.recurring_file,
        )}
        if destination in protected:
            raise ValueError("저장 데이터 파일을 export 출력 경로로 사용할 수 없습니다.")
        if not destination.parent.exists():
            raise ValueError("출력 폴더가 존재하지 않습니다. 폴더를 먼저 만들어주세요.")
        if destination.exists() and destination.is_dir():
            raise ValueError("출력 경로가 디렉토리입니다.")
        count = 0
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", dir=destination.parent,
                prefix=".budget_export_", suffix=".tmp", delete=False,
            ) as file:
                temp_name = file.name
                writer = csv.writer(file)
                writer.writerow(CSV_COLUMNS)
                for tx in self.repo.stream_transactions():
                    if month and tx.date[:7] != month:
                        continue
                    if from_date and tx.date < from_date:
                        continue
                    if to_date and tx.date > to_date:
                        continue
                    writer.writerow([tx.date, tx.type, tx.category, tx.amount, tx.memo, ",".join(tx.tags)])
                    count += 1
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_name, destination)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
        print(f"[완료] {destination} ({count} records)")
        return count

    def import_csv(self, in_path: str) -> tuple[int, int]:
        if not Path(in_path).is_file():
            raise FileNotFoundError(f"가져올 파일을 찾을 수 없습니다: {in_path}")
        imported = skipped = 0
        with open(in_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or any(c not in reader.fieldnames for c in CSV_COLUMNS[:4]):
                raise ValueError("CSV 필수 헤더(date,type,category,amount)가 없습니다.")
            for row_number, row in enumerate(reader, 2):
                try:
                    if None in row:  # 필드 수 초과
                        raise ValueError("CSV 열 개수가 맞지 않습니다.")
                    amount_text = row["amount"]
                    if amount_text is None or not amount_text.isascii() or not amount_text.isdecimal():
                        raise ValueError("금액은 양의 정수여야 합니다.")
                    amount = int(amount_text)
                    date = row["date"]
                    type_val = row["type"]
                    category = row["category"]
                    self._validated_fields(date, type_val, category, amount)
                    memo = row.get("memo") or ""
                    tags_str = row.get("tags") or ""
                    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                    self.repo.add_transaction(Transaction(
                        id=self.generate_id(), date=date, type=type_val,
                        category=category, amount=amount, memo=memo, tags=tags,
                    ))
                    imported += 1
                except (ValueError, TypeError, KeyError) as error:
                    skipped += 1
                    print(f"[건너뜀] CSV {row_number}행: {error}")
        print(f"[완료] imported={imported}, skipped={skipped}")
        return imported, skipped

    def add_recurring(
        self, type_val: str, category: str, amount: int,
        day: int, start_month: str, memo: str = "", tags: list[str] | None = None,
    ) -> str:
        validate_month(start_month)
        if type_val not in ("income", "expense"):
            raise ValueError("타입은 income 또는 expense여야 합니다.")
        if category not in self.repo.get_categories():
            raise ValueError(f"등록되지 않은 카테고리입니다: {category}")
        positive_amount(amount)
        if not 1 <= day <= 31:
            raise ValueError("반복일은 1부터 31 사이여야 합니다.")
        rule = RecurringRule(
            id="RR-" + uuid.uuid4().hex, type=type_val, category=category,
            amount=amount, day=day, start_month=start_month, memo=memo, tags=tags or [],
        )
        self.repo.add_recurring(rule)
        return rule.id

    def list_recurring(self) -> list[RecurringRule]:
        return list(self.repo.stream_recurring())

    def generate_recurring(self, month: str) -> tuple[int, int]:
        validate_month(month)
        existing = {tx.recurring_key for tx in self.repo.stream_transactions() if tx.recurring_key}
        generated: list[Transaction] = []
        skipped = 0
        year, number = map(int, month.split("-"))
        last_day = calendar.monthrange(year, number)[1]
        for rule in self.repo.stream_recurring():
            if rule.start_month > month:
                continue
            key = f"{rule.id}:{month}"
            if key in existing:
                skipped += 1
                continue
            day = min(rule.day, last_day)
            generated.append(Transaction(
                id=self.generate_id(), type=rule.type, category=rule.category,
                amount=rule.amount, date=f"{month}-{day:02d}", memo=rule.memo,
                tags=list(rule.tags), recurring_key=key,
            ))
            existing.add(key)
        count = self.repo.add_transactions(generated)
        print(f"[완료] generated={count}, skipped={skipped}")
        return count, skipped

    def backup(self) -> str:
        directory = self.repo.backup()
        print(f"[백업 완료] 경로: {directory}")
        return directory

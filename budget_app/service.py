import csv
import os
from datetime import datetime
from typing import List, Optional
from .models import Transaction
from .repository import StorageRepository

class BudgetService:
    def __init__(self, data_dir: str = "./data"):
        self.repo = StorageRepository(data_dir)

    def generate_id(self) -> str:
        txs = self.repo.get_all_transactions()
        if not txs:
            return "TX-000001"
        max_num = 0
        for t in txs:
            if t.id.startswith("TX-"):
                try:
                    num = int(t.id.split("-")[1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"TX-{max_num + 1:06d}"

    def add_transaction(self, date: str, type_val: str, category: str, amount: int, memo: str, tags: List[str]) -> str:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")
        
        if type_val not in ["income", "expense"]:
            raise ValueError("타입은 income 또는 expense여야 합니다.")
        
        cats = self.repo.get_categories()
        if category not in cats:
            raise ValueError(f"존재하지 않는 카테고리입니다: {category}. 먼저 카테고리를 추가해주세요.")
        
        if amount <= 0:
            raise ValueError("금액은 양수여야 합니다.")

        tx_id = self.generate_id()
        tx = Transaction(id=tx_id, type=type_val, date=date, amount=amount, category=category, memo=memo, tags=tags)
        self.repo.add_transaction(tx)
        return tx_id

    def list_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        txs = sorted(self.repo.stream_transactions(), key=lambda x: x.date, reverse=True)
        if limit is not None:
            return txs[:limit]
        return txs

    def search_transactions(self, from_date: Optional[str], to_date: Optional[str], category: Optional[str], type_val: Optional[str], q: Optional[str], tag: Optional[str]) -> List[Transaction]:
        txs = []
        for t in self.repo.stream_transactions():
            if from_date and t.date < from_date:
                continue
            if to_date and t.date > to_date:
                continue
            if category and t.category != category:
                continue
            if type_val and t.type != type_val:
                continue
            if q and q.lower() not in t.memo.lower():
                continue
            if tag and tag not in t.tags:
                continue
            txs.append(t)
        return sorted(txs, key=lambda x: x.date, reverse=True)

    def update_transaction(self, tx_id: str, date: Optional[str], type_val: Optional[str], category: Optional[str], amount: Optional[int], memo: Optional[str], tags: Optional[List[str]]) -> bool:
        txs = self.repo.get_all_transactions()
        found = False
        for t in txs:
            if t.id == tx_id:
                found = True
                if date is not None:
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")
                    t.date = date
                if type_val is not None:
                    if type_val not in ["income", "expense"]:
                        raise ValueError("타입은 income 또는 expense여야 합니다.")
                    t.type = type_val
                if category is not None:
                    if category not in self.repo.get_categories():
                        raise ValueError(f"존재하지 않는 카테고리입니다: {category}")
                    t.category = category
                if amount is not None:
                    if amount <= 0:
                        raise ValueError("금액은 양수여야 합니다.")
                    t.amount = amount
                if memo is not None:
                    t.memo = memo
                if tags is not None:
                    t.tags = tags
                break
        if not found:
            return False
        self.repo.save_all_transactions(txs)
        return True

    def delete_transaction(self, tx_id: str) -> bool:
        txs = self.repo.get_all_transactions()
        new_txs = [t for t in txs if t.id != tx_id]
        if len(new_txs) == len(txs):
            return False
        self.repo.save_all_transactions(new_txs)
        return True

    def summary(self, month: str, top_n: int = 3):
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("월 형식은 YYYY-MM이어야 합니다.")

        total_income = 0
        total_expense = 0
        cat_expenses = {}

        for t in self.repo.stream_transactions():
            if t.date.startswith(month):
                if t.type == "income":
                    total_income += t.amount
                elif t.type == "expense":
                    total_expense += t.amount
                    cat_expenses[t.category] = cat_expenses.get(t.category, 0) + t.amount

        balance = total_income - total_expense
        budget = self.repo.get_budget(month)

        print(f"총 수입: {total_income}원")
        print(f"총 지출: {total_expense}원")
        print(f"잔액: {balance}원")

        if budget is not None:
            usage_pct = (total_expense / budget) * 100 if budget > 0 else 0
            print(f"예산: {budget}원 (사용률 {usage_pct:.1f}%)")
            if total_expense > budget:
                print("[경고] 예산을 초과했습니다!")
        else:
            print("예산: 미설정")

        print(f"\n지출 TOP {top_n}")
        sorted_cats = sorted(cat_expenses.items(), key=lambda x: x[1], reverse=True)
        for i, (cat, amt) in enumerate(sorted_cats[:top_n], 1):
            print(f"{i}) {cat} {amt}원")
        if not sorted_cats:
            print("데이터 없음")

    def set_budget(self, month: str, amount: int):
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("월 형식은 YYYY-MM이어야 합니다.")
        if amount < 0:
            raise ValueError("예산 금액은 0 이상이어야 합니다.")
        self.repo.set_budget(month, amount)

    def manage_category(self, action: str, name: Optional[str] = None):
        if action == "list":
            cats = self.repo.get_categories()
            print("등록된 카테고리:")
            for c in cats:
                print(f"- {c}")
        elif action == "add":
            if not name:
                raise ValueError("추가할 카테고리 이름을 입력해주세요.")
            success = self.repo.add_category(name)
            if success:
                print(f"[저장 완료] category={name}")
            else:
                print(f"[알림] 이미 존재하는 카테고리입니다: {name}")
        elif action == "remove":
            if not name:
                raise ValueError("삭제할 카테고리 이름을 입력해주세요.")
            used = any(t.category == name for t in self.repo.stream_transactions())
            if used:
                raise ValueError(f"해당 카테고리({name})를 사용하는 내역이 존재하여 삭제할 수 없습니다.")
            self.repo.remove_category(name)
            print(f"[삭제 완료] category={name}")

    def export_csv(self, out_path: str, month: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None):
        if not month and not (from_date and to_date):
            raise ValueError("export는 --month 또는 (--from과 --to) 조건 중 하나 이상을 필수로 받아야 합니다.")
        
        txs = self.repo.get_all_transactions()
        filtered = []
        for t in txs:
            if month and not t.date.startswith(month):
                continue
            if from_date and t.date < from_date:
                continue
            if to_date and t.date > to_date:
                continue
            filtered.append(t)

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
            for t in filtered:
                writer.writerow([t.date, t.type, t.category, t.amount, t.memo, ",".join(t.tags)])
        print(f"[완료] {out_path} ({len(filtered)} records)")

    def import_csv(self, in_path: str):
        if not os.path.exists(in_path):
            raise FileNotFoundError(f"가져올 파일을 찾을 수 없습니다: {in_path}")
        
        imported = 0
        skipped = 0
        cats = self.repo.get_categories()

        with open(in_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = row["date"]
                    t_type = row["type"]
                    category = row["category"]
                    amount = int(row["amount"])
                    memo = row.get("memo", "")
                    tags_str = row.get("tags", "")
                    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

                    datetime.strptime(date, "%Y-%m-%d")
                    if t_type not in ["income", "expense"]:
                        skipped += 1
                        continue
                    if category not in cats:
                        skipped += 1
                        continue
                    if amount <= 0:
                        skipped += 1
                        continue

                    tx_id = self.generate_id()
                    tx = Transaction(id=tx_id, type=t_type, date=date, amount=amount, category=category, memo=memo, tags=tags)
                    self.repo.add_transaction(tx)
                    imported += 1
                except Exception:
                    skipped += 1

        print(f"[완료] imported={imported}, skipped={skipped}")

    def backup(self):
        b_dir = self.repo.backup()
        print(f"[백업 완료] 경로: {b_dir}")
import csv
from datetime import datetime
from typing import List, Optional, Dict, Generator, Tuple, Any
from .models import Transaction, Category, Budget
from .repository import Repository
from .decorators import handle_exceptions, measure_time


class BudgetService:
    """가계부 비즈니스 로직을 처리하는 서비스 클래스"""
    def __init__(self, data_dir: str = "./data") -> None:
        self.repo = Repository(data_dir)

    def generate_id(self) -> str:
        """유일한 거래 ID를 생성합니다 (예: TX-000012)."""
        txs = self.repo.get_all_transactions()
        if not txs:
            return "TX-000001"
        max_num = 0
        for tx in txs:
            if tx.id.startswith("TX-"):
                try:
                    num = int(tx.id.split("-")[1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        return f"TX-{max_num + 1:06d}"

    def add_transaction(self, tx_type: str, date: str, amount: int, category: str, memo: str, tags: List[str]) -> str:
        """새로운 거래를 추가합니다."""
        if tx_type not in ["income", "expense"]:
            raise ValueError("타입은 income 또는 expense여야 합니다.")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")
        if amount <= 0:
            raise ValueError("금액은 양수여야 합니다.")
        
        categories = self.repo.get_categories()
        if category not in categories:
            raise ValueError(f"존재하지 않는 카테고리입니다: {category}. 먼저 카테고리를 등록해주세요.")

        tx_id = self.generate_id()
        tx = Transaction(id=tx_id, type=tx_type, date=date, amount=amount, category=category, memo=memo, tags=tags)
        self.repo.save_transaction(tx)
        return tx_id

    # @measure_time
    def list_transactions(self, limit: Optional[int] = None) -> Generator[Transaction, None, None]:
        """최신순으로 거래 내역을 스트리밍 조회합니다."""
        txs = self.repo.get_all_transactions()
        txs.sort(key=lambda x: (x.date, x.id), reverse=True)
        count = 0
        for tx in txs:
            yield tx
            count += 1
            if limit is not None and count >= limit:
                break

    def search_transactions(self, from_date: Optional[str] = None, to_date: Optional[str] = None, 
                            category: Optional[str] = None, tx_type: Optional[str] = None, 
                            q: Optional[str] = None, tag: Optional[str] = None) -> List[Transaction]:
        """조건에 맞는 거래를 검색하여 최신순으로 반환합니다."""
        results = []
        for tx in self.repo.stream_transactions():
            if from_date and tx.date < from_date:
                continue
            if to_date and tx.date > to_date:
                continue
            if category and tx.category != category:
                continue
            if tx_type and tx.type != tx_type:
                continue
            if q and q.lower() not in tx.memo.lower():
                continue
            if tag and tag not in tx.tags:
                continue
            results.append(tx)
        
        results.sort(key=lambda x: (x.date, x.id), reverse=True)
        return results

    def update_transaction(self, tx_id: str, date: Optional[str] = None, tx_type: Optional[str] = None,
                           category: Optional[str] = None, amount: Optional[int] = None,
                           memo: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """기존 거래 내역을 수정합니다."""
        txs = self.repo.get_all_transactions()
        found = False
        for tx in txs:
            if tx.id == tx_id:
                if date:
                    datetime.strptime(date, "%Y-%m-%d")
                    tx.date = date
                if tx_type:
                    if tx_type not in ["income", "expense"]:
                        raise ValueError("타입은 income 또는 expense여야 합니다.")
                    tx.type = tx_type
                if category:
                    if category not in self.repo.get_categories():
                        raise ValueError("존재하지 않는 카테고리입니다.")
                    tx.category = category
                if amount is not None:
                    if amount <= 0:
                        raise ValueError("금액은 양수여야 합니다.")
                    tx.amount = amount
                if memo is not None:
                    tx.memo = memo
                if tags is not None:
                    tx.tags = tags
                found = True
                break
        
        if not found:
            return False
        
        self.repo.save_all_transactions(txs)
        return True

    def delete_transaction(self, tx_id: str) -> bool:
        """특정 ID의 거래를 삭제합니다."""
        txs = self.repo.get_all_transactions()
        new_txs = [tx for tx in txs if tx.id != tx_id]
        if len(new_txs) == len(txs):
            return False
        self.repo.save_all_transactions(new_txs)
        return True

    def summary_month(self, month: str, top_n: int = 3) -> Dict[str, Any]:
        """월별 요약 정보를 계산합니다."""
        txs = [tx for tx in self.repo.stream_transactions() if tx.date.startswith(month)]
        
        total_income = sum(tx.amount for tx in txs if tx.type == "income")
        total_expense = sum(tx.amount for tx in txs if tx.type == "expense")
        balance = total_income - total_expense
        
        cat_expense: Dict[str, int] = {}
        for tx in txs:
            if tx.type == "expense":
                cat_expense[tx.category] = cat_expense.get(tx.category, 0) + tx.amount
                
        sorted_top = sorted(cat_expense.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        budget_amt = self.repo.get_budget(month)
        usage_pct = None
        if budget_amt and budget_amt > 0:
            usage_pct = (total_expense / budget_amt) * 100

        return {
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "budget": budget_amt,
            "usage_pct": usage_pct,
            "top_expenses": sorted_top,
            "has_data": len(txs) > 0
        }

    def add_category(self, name: str) -> None:
        cats = self.repo.get_categories()
        if name in cats:
            raise ValueError("이미 존재하는 카테고리입니다.")
        self.repo.save_category(Category(name=name))

    def list_categories(self) -> List[str]:
        return self.repo.get_categories()

    def remove_category(self, name: str, fallback_category: Optional[str] = None) -> None:
        cats = self.repo.get_categories()
        if name not in cats:
            raise ValueError("존재하지 않는 카테고리입니다.")
        
        txs = self.repo.get_all_transactions()
        used = any(tx.category == name for tx in txs)
        if used:
            if not fallback_category or fallback_category not in cats:
                raise ValueError("해당 카테고리를 사용하는 거래 내역이 있습니다. 대체 카테고리를 지정해주세요.")
            for tx in txs:
                if tx.category == name:
                    tx.category = fallback_category
            self.repo.save_all_transactions(txs)
            
        self.repo.remove_category(name)

    def set_budget(self, month: str, amount: int) -> None:
        if amount < 0:
            raise ValueError("예산 금액은 0 이상이어야 합니다.")
        self.repo.set_budget(month, amount)

    def export_csv(self, filename: str, month: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None) -> int:
        """조건에 맞는 거래 내역을 CSV로 내보냅니다."""
        txs = []
        for tx in self.repo.stream_transactions():
            if month and not tx.date.startswith(month):
                continue
            if from_date and tx.date < from_date:
                continue
            if to_date and tx.date > to_date:
                continue
            txs.append(tx)
            
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
            for tx in txs:
                writer.writerow([
                    tx.date,
                    tx.type,
                    tx.category,
                    tx.amount,
                    tx.memo,
                    ",".join(tx.tags)
                ])
        return len(txs)

    def import_csv(self, filename: str) -> Tuple[int, int]:
        """CSV 파일로부터 거래 내역을 가져옵니다."""
        imported = 0
        skipped = 0
        categories = self.repo.get_categories()
        
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = row["date"]
                    tx_type = row["type"]
                    category = row["category"]
                    amount = int(row["amount"])
                    memo = row.get("memo", "")
                    tags_str = row.get("tags", "")
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                    
                    if category not in categories or tx_type not in ["income", "expense"] or amount <= 0:
                        skipped += 1
                        continue
                        
                    self.add_transaction(tx_type, date, amount, category, memo, tags)
                    imported += 1
                except Exception:
                    skipped += 1
                    
        return imported, skipped
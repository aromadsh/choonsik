import json
import os
from pathlib import Path
from typing import Generator, List, Dict, Any, Optional
from .models import Transaction, Category, Budget

class Repository:
    """JSONL 기반 파일 I/O 및 스트리밍 처리 저장소 클래스"""
    def __init__(self, data_dir: str = "./data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tx_file = self.data_dir / "transactions.jsonl"
        self.cat_file = self.data_dir / "categories.jsonl"
        self.budget_file = self.data_dir / "budgets.jsonl"
        
        self._init_files()

    def _init_files(self) -> None:
        """필요한 파일이 없으면 생성하고, 카테고리가 비어있으면 기본 카테고리를 초기화합니다."""
        if not self.tx_file.exists():
            self.tx_file.touch()
        if not self.budget_file.exists():
            self.budget_file.touch()
            
        if not self.cat_file.exists():
            self.cat_file.touch()
            self.init_default_categories()
        else:
            if self.cat_file.stat().st_size == 0:
                self.init_default_categories()

    def init_default_categories(self) -> None:
        """기본 카테고리 초기 생성"""
        defaults = ["food", "transport", "rent", "salary", "etc"]
        for cat in defaults:
            self.save_category(Category(name=cat))

    def get_categories(self) -> List[str]:
        """등록된 모든 카테고리 목록을 반환합니다."""
        categories = []
        if not self.cat_file.exists():
            return categories
        with open(self.cat_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    categories.append(data["name"])
        return categories

    def save_category(self, category: Category) -> None:
        """새로운 카테고리를 추가합니다."""
        with open(self.cat_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"name": category.name}, ensure_ascii=False) + "\n")

    def remove_category(self, name: str) -> None:
        """카테고리를 삭제합니다 (원자적 쓰기 적용)."""
        categories = self.get_categories()
        if name in categories:
            categories.remove(name)
        
        temp_file = self.cat_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            for cat in categories:
                f.write(json.dumps({"name": cat}, ensure_ascii=False) + "\n")
        os.replace(temp_file, self.cat_file)

    def stream_transactions(self) -> Generator[Transaction, None, None]:
        """파일 전체를 한 번에 올리지 않고, 제너레이터를 통해 한 줄씩 스트리밍 읽기합니다."""
        if not self.tx_file.exists():
            return
        with open(self.tx_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    yield Transaction(
                        id=data["id"],
                        type=data["type"],
                        date=data["date"],
                        amount=data["amount"],
                        category=data["category"],
                        memo=data.get("memo", ""),
                        tags=data.get("tags", [])
                    )

    def get_all_transactions(self) -> List[Transaction]:
        """모든 거래 내역을 리스트로 반환합니다."""
        return list(self.stream_transactions())

    def save_transaction(self, tx: Transaction) -> None:
        """거래 내역을 추가합니다."""
        with open(self.tx_file, "a", encoding="utf-8") as f:
            data = {
                "id": tx.id,
                "type": tx.type,
                "date": tx.date,
                "amount": tx.amount,
                "category": tx.category,
                "memo": tx.memo,
                "tags": tx.tags
            }
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def save_all_transactions(self, txs: List[Transaction]) -> None:
        """수정/삭제 등으로 변경된 전체 거래 목록을 원자적으로 덮어씁니다."""
        temp_file = self.tx_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            for tx in txs:
                data = {
                    "id": tx.id,
                    "type": tx.type,
                    "date": tx.date,
                    "amount": tx.amount,
                    "category": tx.category,
                    "memo": tx.memo,
                    "tags": tx.tags
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        os.replace(temp_file, self.tx_file)

    def get_budget(self, month: str) -> Optional[int]:
        """특정 월(YYYY-MM)의 예산 금액을 조회합니다."""
        if not self.budget_file.exists():
            return None
        with open(self.budget_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data["month"] == month:
                        return data["amount"]
        return None

    def set_budget(self, month: str, amount: int) -> None:
        """월별 예산을 설정하거나 갱신합니다 (원자적 쓰기 적용)."""
        budgets: Dict[str, int] = {}
        if self.budget_file.exists():
            with open(self.budget_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        budgets[data["month"]] = data["amount"]
        
        budgets[month] = amount
        
        temp_file = self.budget_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            for m, amt in budgets.items():
                f.write(json.dumps({"month": m, "amount": amt}, ensure_ascii=False) + "\n")
        os.replace(temp_file, self.budget_file)
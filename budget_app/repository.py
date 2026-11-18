import os
import json
import shutil
from datetime import datetime
from typing import Generator, List, Dict, Optional
from .models import Transaction, Category

class StorageRepository:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.trans_file = os.path.join(self.data_dir, "transactions.jsonl")
        self.cat_file = os.path.join(self.data_dir, "categories.jsonl")
        self.budget_file = os.path.join(self.data_dir, "budgets.jsonl")
        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.cat_file):
            default_cats = ["food", "transport", "rent", "salary", "entertainment", "other"]
            self.save_categories([Category(name=c) for c in default_cats])
        if not os.path.exists(self.trans_file):
            open(self.trans_file, "w", encoding="utf-8").close()
        if not os.path.exists(self.budget_file):
            open(self.budget_file, "w", encoding="utf-8").close()

    def _atomic_write(self, filepath: str, lines: List[str]):
        tmp_file = filepath + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        os.replace(tmp_file, filepath)

    def stream_transactions(self) -> Generator[Transaction, None, None]:
        if not os.path.exists(self.trans_file):
            return
        with open(self.trans_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield Transaction.from_dict(data)
                except json.JSONDecodeError:
                    continue

    def get_all_transactions(self) -> List[Transaction]:
        return list(self.stream_transactions())

    def save_all_transactions(self, transactions: List[Transaction]):
        lines = [json.dumps(t.to_dict(), ensure_ascii=False) for t in transactions]
        self._atomic_write(self.trans_file, lines)

    def add_transaction(self, tx: Transaction):
        txs = self.get_all_transactions()
        txs.append(tx)
        self.save_all_transactions(txs)

    def get_categories(self) -> List[str]:
        if not os.path.exists(self.cat_file):
            return []
        cats = []
        with open(self.cat_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        cats.append(data["name"])
                    except:
                        pass
        return cats

    def save_categories(self, categories: List[Category]):
        lines = [json.dumps({"name": c.name}, ensure_ascii=False) for c in categories]
        self._atomic_write(self.cat_file, lines)

    def add_category(self, name: str) -> bool:
        cats = self.get_categories()
        if name in cats:
            return False
        cats.append(name)
        self.save_categories([Category(name=c) for c in cats])
        return True

    def remove_category(self, name: str):
        cats = self.get_categories()
        if name in cats:
            cats.remove(name)
            self.save_categories([Category(name=c) for c in cats])

    def get_budgets(self) -> Dict[str, int]:
        if not os.path.exists(self.budget_file):
            return {}
        budgets = {}
        with open(self.budget_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        budgets[data["month"]] = int(data["amount"])
                    except:
                        pass
        return budgets

    def set_budget(self, month: str, amount: int):
        budgets = self.get_budgets()
        budgets[month] = amount
        lines = [json.dumps({"month": m, "amount": a}, ensure_ascii=False) for m, a in budgets.items()]
        self._atomic_write(self.budget_file, lines)

    def get_budget(self, month: str) -> Optional[int]:
        return self.get_budgets().get(month)

    def backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.data_dir, f"backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        for fname in ["transactions.jsonl", "categories.jsonl", "budgets.jsonl"]:
            src = os.path.join(self.data_dir, fname)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(backup_dir, fname))
        return backup_dir
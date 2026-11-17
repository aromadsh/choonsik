import argparse
import sys
from typing import List
from .service import BudgetService
from .decorators import handle_exceptions

@handle_exceptions
def main() -> None:
    """CLI 메인 진입점 함수"""
    parser = argparse.ArgumentParser(description="콘솔 가계부 프로그램 (소규모 서비스)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. add
    subparsers.add_parser("add", help="새로운 거래 추가 (대화형)")

    # 2. list
    list_parser = subparsers.add_parser("list", help="거래 목록 조회")
    list_parser.add_argument("--limit", type=int, default=None, help="출력할 최대 개수")

    # 3. search
    search_parser = subparsers.add_parser("search", help="조건별 거래 검색")
    search_parser.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--to", dest="to_date", help="종료 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--category", help="카테고리")
    search_parser.add_argument("--type", help="타입 (income/expense)")
    search_parser.add_argument("--q", help="메모 키워드 검색")
    search_parser.add_argument("--tag", help="태그 검색")

    # 4. summary
    summary_parser = subparsers.add_parser("summary", help="월별 요약 및 예산 확인")
    summary_parser.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=3, help="상위 카테고리 수 (기본 3)")

    # 5. budget
    budget_parser = subparsers.add_parser("budget", help="예산 설정")
    budget_subparsers = budget_parser.add_subparsers(dest="budget_action", required=True)
    set_budget_parser = budget_subparsers.add_parser("set", help="월 예산 설정")
    set_budget_parser.add_argument("--month", required=True, help="월 (YYYY-MM)")
    set_budget_parser.add_argument("--amount", type=int, required=True, help="예산 금액")

    # 6. category
    cat_parser = subparsers.add_parser("category", help="카테고리 관리")
    cat_subparsers = cat_parser.add_subparsers(dest="cat_action", required=True)
    cat_subparsers.add_parser("list", help="카테고리 목록 조회")
    cat_subparsers.add_parser("add", help="카테고리 추가")
    remove_cat_parser = cat_subparsers.add_parser("remove", help="카테고리 삭제")
    remove_cat_parser.add_argument("--name", required=True, help="삭제할 카테고리명")
    remove_cat_parser.add_argument("--fallback", help="대체 카테고리명 (사용 중인 내역이 있을 경우)")

    # 7. update
    update_parser = subparsers.add_parser("update", help="거래 수정")
    update_parser.add_argument("--id", required=True, help="수정할 거래 ID")
    update_parser.add_argument("--date", help="새 날짜 (YYYY-MM-DD)")
    update_parser.add_argument("--type", help="새 타입 (income/expense)")
    update_parser.add_argument("--category", help="새 카테고리")
    update_parser.add_argument("--amount", type=int, help="새 금액")
    update_parser.add_argument("--memo", help="새 메모")
    update_parser.add_argument("--tag", help="새 태그 (쉼표 구분)")

    # 8. delete
    delete_parser = subparsers.add_parser("delete", help="거래 삭제")
    delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")

    # 9. export / import
    export_parser = subparsers.add_parser("export", help="CSV 내보내기")
    export_parser.add_argument("--out", required=True, help="저장할 CSV 파일명")
    export_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    export_parser.add_argument("--from", dest="from_date", help="시작 날짜")
    export_parser.add_argument("--to", dest="to_date", help="종료 날짜")

    import_parser = subparsers.add_parser("import", help="CSV 가져오기")
    import_parser.add_argument("--from", dest="from_file", required=True, help="가져올 CSV 파일명")

    args = parser.parse_args()
    service = BudgetService()

    if args.command == "add":
        print("--- 거래 추가 ---")
        date = input("날짜(YYYY-MM-DD): ").strip()
        tx_type = input("타입(income/expense): ").strip()
        print(f"등록된 카테고리 목록: {service.list_categories()}")
        category = input("카테고리: ").strip()
        amount_str = input("금액(양수): ").strip()
        amount = int(amount_str)
        memo = input("메모(선택): ").strip()
        tags_str = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        tx_id = service.add_transaction(tx_type, date, amount, category, memo, tags)
        print(f"[저장 완료] id={tx_id}")

    elif args.command == "list":
        for tx in service.list_transactions(limit=args.limit):
            memo_str = f" | {tx.memo}" if tx.memo else ""
            tag_str = f" [tags: {', '.join(tx.tags)}]" if tx.tags else ""
            print(f"{tx.id} | {tx.date} | {tx.type.ljust(7)} | {tx.category.ljust(10)} | {tx.amount}원{memo_str}{tag_str}")

    elif args.command == "search":
        results = service.search_transactions(
            from_date=args.from_date,
            to_date=args.to_date,
            category=args.category,
            tx_type=args.type,
            q=args.q,
            tag=args.tag
        )
        for tx in results:
            print(f"{tx.id} | {tx.date} | {tx.type} | {tx.category} | {tx.amount}원 | {tx.memo}")
        print(f"[검색 완료] 총 {len(results)}건")

    elif args.command == "summary":
        res = service.summary_month(args.month, top_n=args.top)
        if not res["has_data"]:
            print(f"[{args.month}] 데이터 없음")
            return
        print(f"총 수입: {res['total_income']}원")
        print(f"총 지출: {res['total_expense']}원")
        print(f"잔액: {res['balance']}원")
        if res["budget"] is not None:
            status = f"예산: {res['budget']}원 (사용률 {res['usage_pct']:.1f}%)"
            if res["usage_pct"] > 100:
                status += " [경고] 예산 초과!"
            print(status)
        else:
            print("예산: 미설정")
        
        print(f"\n지출 TOP {args.top}")
        for idx, (cat, amt) in enumerate(res["top_expenses"], 1):
            print(f"{idx}) {cat} {amt}원")

    elif args.command == "budget":
        if args.budget_action == "set":
            service.set_budget(args.month, args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount}원 설정됨")

    elif args.command == "category":
        if args.cat_action == "list":
            for cat in service.list_categories():
                print(cat)
        elif args.cat_action == "add":
            name = input("카테고리명: ").strip()
            service.add_category(name)
            print(f"[저장 완료] category={name}")
        elif args.cat_action == "remove":
            try:
                service.remove_category(args.name, fallback_category=args.fallback)
                print(f"[삭제 완료] category={args.name}")
            except ValueError as e:
                print(f"[안내] {e}")
                fallback = input("대체할 카테고리명을 입력하세요: ").strip()
                service.remove_category(args.name, fallback_category=fallback)
                print(f"[삭제 완료] category={args.name} (대체: {fallback})")

    elif args.command == "update":
        tags = [t.strip() for t in args.tag.split(",")] if args.tag else None
        success = service.update_transaction(
            tx_id=args.id,
            date=args.date,
            tx_type=args.type,
            category=args.category,
            amount=args.amount,
            memo=args.memo,
            tags=tags
        )
        if success:
            print(f"[수정 완료] id={args.id}")
        else:
            print(f"[오류] 존재하지 않는 거래 ID입니다: {args.id}")

    elif args.command == "delete":
        success = service.delete_transaction(args.id)
        if success:
            print(f"[삭제 완료] id={args.id}")
        else:
            print(f"[오류] 존재하지 않는 거래 ID입니다: {args.id}")

    elif args.command == "export":
        if not (args.month or (args.from_date and args.to_date)):
            print("[오류] --month 또는 (--from과 --to) 중 하나 이상 조건을 지정해야 합니다.")
            sys.exit(1)
        count = service.export_csv(args.out, month=args.month, from_date=args.from_date, to_date=args.to_date)
        print(f"[완료] {args.out} ({count} records)")

    elif args.command == "import":
        imported, skipped = service.import_csv(args.from_file)
        print(f"[완료] imported={imported}, skipped={skipped}")
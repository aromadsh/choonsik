import argparse
from .decorators import handle_exceptions
from .service import BudgetService

@handle_exceptions
def main():
    parser = argparse.ArgumentParser(description="나만의 용돈 기입장 프로그램")
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")

    # add
    subparsers.add_parser("add", help="거래 추가")

    # list
    list_parser = subparsers.add_parser("list", help="거래 목록 조회")
    list_parser.add_argument("--limit", type=int, default=None, help="조회할 최대 개수")

    # search
    search_parser = subparsers.add_parser("search", help="거래 조건 검색")
    search_parser.add_argument("--from", dest="from_date", help="시작일 (YYYY-MM-DD)")
    search_parser.add_argument("--to", dest="to_date", help="종료일 (YYYY-MM-DD)")
    search_parser.add_argument("--category", help="카테고리")
    search_parser.add_argument("--type", help="타입 (income/expense)")
    search_parser.add_argument("--q", help="메모 검색어")
    search_parser.add_argument("--tag", help="태그")

    # summary
    summary_parser = subparsers.add_parser("summary", help="월별 요약")
    summary_parser.add_argument("--month", required=True, help="월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=3, help="TOP N 카테고리")

    # budget
    budget_parser = subparsers.add_parser("budget", help="예산 설정")
    budget_sub = budget_parser.add_subparsers(dest="budget_command")
    set_budget_parser = budget_sub.add_parser("set", help="예산 지정")
    set_budget_parser.add_argument("--month", required=True, help="월 (YYYY-MM)")
    set_budget_parser.add_argument("--amount", required=True, type=int, help="금액")

    # category
    cat_parser = subparsers.add_parser("category", help="카테고리 관리")
    cat_sub = cat_parser.add_subparsers(dest="cat_command")
    cat_sub.add_parser("list", help="카테고리 목록")
    add_cat_parser = cat_sub.add_parser("add", help="카테고리 추가")
    add_cat_parser.add_argument("--name", help="카테고리명")
    rem_cat_parser = cat_sub.add_parser("remove", help="카테고리 삭제")
    rem_cat_parser.add_argument("--name", help="삭제할 카테고리명")

    # update
    update_parser = subparsers.add_parser("update", help="거래 수정")
    update_parser.add_argument("--id", required=True, help="거래 ID")
    update_parser.add_argument("--date", help="날짜 (YYYY-MM-DD)")
    update_parser.add_argument("--type", help="타입 (income/expense)")
    update_parser.add_argument("--category", help="카테고리")
    update_parser.add_argument("--amount", type=int, help="금액")
    update_parser.add_argument("--memo", help="메모")
    update_parser.add_argument("--tags", help="태그 (쉼표 구분)")

    # delete
    del_parser = subparsers.add_parser("delete", help="거래 삭제")
    del_parser.add_argument("--id", required=True, help="거래 ID")

    # export
    exp_parser = subparsers.add_parser("export", help="CSV 내보내기")
    exp_parser.add_argument("--out", required=True, help="저장할 파일 경로")
    exp_parser.add_argument("--month", help="월 (YYYY-MM)")
    exp_parser.add_argument("--from", dest="from_date", help="시작일")
    exp_parser.add_argument("--to", dest="to_date", help="종료일")

    # import
    imp_parser = subparsers.add_parser("import", help="CSV 가져오기")
    imp_parser.add_argument("--from", dest="from_path", required=True, help="가져올 CSV 파일 경로")

    # backup
    subparsers.add_parser("backup", help="타임스탬프 백업 생성")

    args = parser.parse_args()
    service = BudgetService()

    if not args.command:
        parser.print_help()
        return

    if args.command == "add":
        print("--- 거래 추가 ---")
        date = input("날짜(YYYY-MM-DD): ").strip()
        t_type = input("타입(income/expense): ").strip()
        category = input("카테고리: ").strip()
        amount_str = input("금액(양수): ").strip()
        amount = int(amount_str)
        memo = input("메모(선택): ").strip()
        tags_input = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        tx_id = service.add_transaction(date, t_type, category, amount, memo, tags)
        print(f"[저장 완료] id={tx_id}")

    elif args.command == "list":
        txs = service.list_transactions(limit=args.limit)
        for t in txs:
            tags_str = f" | tags: {','.join(t.tags)}" if t.tags else ""
            memo_str = f" | {t.memo}" if t.memo else ""
            print(f"{t.id} | {t.date} | {t.type} | {t.category} | {t.amount}원{memo_str}{tags_str}")

    elif args.command == "search":
        txs = service.search_transactions(
            from_date=args.from_date,
            to_date=args.to_date,
            category=args.category,
            type_val=args.type,
            q=args.q,
            tag=args.tag
        )
        for t in txs:
            tags_str = f" | tags: {','.join(t.tags)}" if t.tags else ""
            memo_str = f" | {t.memo}" if t.memo else ""
            print(f"{t.id} | {t.date} | {t.type} | {t.category} | {t.amount}원{memo_str}{tags_str}")

    elif args.command == "summary":
        service.summary(month=args.month, top_n=args.top)

    elif args.command == "budget":
        if args.budget_command == "set":
            service.set_budget(month=args.month, amount=args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount}원")
        else:
            print("사용법: python -m budget_app budget set --month YYYY-MM --amount 금액")

    elif args.command == "category":
        if args.cat_command == "list":
            service.manage_category("list")
        elif args.cat_command == "add":
            name = args.name
            if not name:
                name = input("카테고리명: ").strip()
            service.manage_category("add", name)
        elif args.cat_command == "remove":
            name = args.name
            if not name:
                name = input("삭제할 카테고리명: ").strip()
            service.manage_category("remove", name)
        else:
            print("사용법: python -m budget_app category [add|list|remove]")

    elif args.command == "update":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        success = service.update_transaction(
            tx_id=args.id,
            date=args.date,
            type_val=args.type,
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
        service.export_csv(
            out_path=args.out,
            month=args.month,
            from_date=args.from_date,
            to_date=args.to_date
        )

    elif args.command == "import":
        service.import_csv(in_path=args.from_path)

    elif args.command == "backup":
        service.backup()

if __name__ == "__main__":
    main()
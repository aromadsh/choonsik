import argparse
from pathlib import Path

from .decorators import handle_exceptions
from .formatting import print_transactions
from .service import BudgetService


def positive_integer(text: str) -> int:
    try:
        number = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요.") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요.")
    return number


def nonnegative_integer(text: str) -> int:
    try:
        number = int(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("0 이상의 정수를 입력하세요.") from error
    if number < 0:
        raise argparse.ArgumentTypeError("0 이상의 정수를 입력하세요.")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="나만의 용돈 기입장 프로그램")
    parser.add_argument("--data-dir", default="./data", help="JSONL 저장 폴더 (기본: ./data)")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("add", help="거래 대화형 추가")

    listing = commands.add_parser("list", help="거래 날짜 최신순 조회")
    listing.add_argument("--limit", type=positive_integer, default=10)

    search = commands.add_parser("search", help="거래 조건 검색")
    search.add_argument("--from", dest="from_date")
    search.add_argument("--to", dest="to_date")
    search.add_argument("--category")
    search.add_argument("--type", choices=["income", "expense"])
    search.add_argument("--q")
    search.add_argument("--tag")

    summary = commands.add_parser("summary", help="월별 요약")
    summary.add_argument("--month", required=True)
    summary.add_argument("--top", type=positive_integer, default=3)

    budget = commands.add_parser("budget", help="예산 설정 및 조회")
    budget_sub = budget.add_subparsers(dest="budget_command", required=True)
    budget_set = budget_sub.add_parser("set", help="월 예산 지정")
    budget_set.add_argument("--month", required=True)
    budget_set.add_argument("--amount", required=True, type=nonnegative_integer)
    budget_show = budget_sub.add_parser("show", help="월 예산 조회")
    budget_show.add_argument("--month", required=True)

    category = commands.add_parser("category", help="카테고리 관리")
    category_sub = category.add_subparsers(dest="category_command", required=True)
    category_sub.add_parser("list", help="카테고리 목록")
    category_add = category_sub.add_parser("add", help="카테고리 추가")
    category_add.add_argument("--name")
    category_remove = category_sub.add_parser("remove", help="카테고리 삭제")
    category_remove.add_argument("--name")

    update = commands.add_parser("update", help="ID 기준 거래 수정 (옵션 방식)")
    update.add_argument("--id", required=True)
    update.add_argument("--date")
    update.add_argument("--type", choices=["income", "expense"])
    update.add_argument("--category")
    update.add_argument("--amount", type=positive_integer)
    update.add_argument("--memo")
    update.add_argument("--tags", help="쉼표 구분, 빈 문자열은 태그 삭제")

    delete = commands.add_parser("delete", help="ID 기준 거래 삭제")
    delete.add_argument("--id", required=True)

    export = commands.add_parser("export", help="거래 CSV 내보내기")
    export.add_argument("--out", required=True)
    export.add_argument("--month")
    export.add_argument("--from", dest="from_date")
    export.add_argument("--to", dest="to_date")

    import_parser = commands.add_parser("import", help="CSV에서 거래 가져오기")
    import_parser.add_argument("--from", dest="from_path", required=True)

    commands.add_parser("backup", help="타임스탬프 포함 백업")

    recurring = commands.add_parser("recurring", help="월간 반복 거래 관리 (보너스)")
    recurring_sub = recurring.add_subparsers(dest="recurring_command", required=True)
    recurring_add = recurring_sub.add_parser("add", help="반복 규칙 등록")
    recurring_add.add_argument("--type", required=True, choices=["income", "expense"])
    recurring_add.add_argument("--category", required=True)
    recurring_add.add_argument("--amount", required=True, type=positive_integer)
    recurring_add.add_argument("--day", required=True, type=positive_integer)
    recurring_add.add_argument("--start-month", required=True)
    recurring_add.add_argument("--memo", default="")
    recurring_add.add_argument("--tags", default="")
    recurring_sub.add_parser("list", help="반복 규칙 조회")
    recurring_generate = recurring_sub.add_parser("generate", help="월별 거래 자동 생성")
    recurring_generate.add_argument("--month", required=True)

    return parser.parse_args()


def _tags(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [tag.strip() for tag in value.split(",") if tag.strip()]


@handle_exceptions
def main() -> int:
    args = parse_args()
    service = BudgetService(args.data_dir)

    if args.command == "add":
        print("--- 거래 추가 ---")
        date = input("날짜(YYYY-MM-DD): ").strip()
        kind = input("타입(income/expense): ").strip()
        category = input("카테고리: ").strip()
        raw_amount = input("금액(양수): ").strip()
        if not raw_amount.isascii() or not raw_amount.isdecimal():
            raise ValueError("금액은 0보다 큰 정수여야 합니다.")
        memo = input("메모(선택): ").strip()
        tags = _tags(input("태그(쉼표 구분, 선택): ").strip()) or []
        tx_id = service.add_transaction(date, kind, category, int(raw_amount), memo, tags)
        print(f"[저장 완료] id={tx_id}")

    elif args.command == "list":
        print_transactions(service.list_transactions(args.limit))

    elif args.command == "search":
        print_transactions(service.search_transactions(
            from_date=args.from_date, to_date=args.to_date,
            category=args.category, type_val=args.type,
            q=args.q, tag=args.tag,
        ))

    elif args.command == "summary":
        service.summary(args.month, args.top)

    elif args.command == "budget":
        if args.budget_command == "set":
            service.set_budget(args.month, args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount}원")
        elif args.budget_command == "show":
            from .validation import validate_month
            validate_month(args.month)
            amount = service.repo.get_budget(args.month)
            print(f"{args.month} 예산: {amount}원" if amount is not None else f"{args.month} 예산: 미설정")

    elif args.command == "category":
        if args.category_command == "list":
            service.manage_category("list")
        else:
            name = args.name or input("카테고리명: ").strip()
            service.manage_category(args.category_command, name)

    elif args.command == "update":
        if service.update_transaction(
            tx_id=args.id, date=args.date, type_val=args.type,
            category=args.category, amount=args.amount,
            memo=args.memo, tags=_tags(args.tags),
        ):
            print(f"[수정 완료] id={args.id}")
        else:
            raise ValueError(f"존재하지 않는 거래 ID입니다: {args.id}")

    elif args.command == "delete":
        if service.delete_transaction(args.id):
            print(f"[삭제 완료] id={args.id}")
        else:
            raise ValueError(f"존재하지 않는 거래 ID입니다: {args.id}")

    elif args.command == "export":
        service.export_csv(args.out, args.month, args.from_date, args.to_date)

    elif args.command == "import":
        service.import_csv(args.from_path)

    elif args.command == "backup":
        service.backup()

    elif args.command == "recurring":
        if args.recurring_command == "add":
            rule_id = service.add_recurring(
                args.type, args.category, args.amount, args.day,
                args.start_month, args.memo, _tags(args.tags),
            )
            print(f"[반복 규칙 등록] id={rule_id}")
        elif args.recurring_command == "list":
            rules = service.list_recurring()
            for rule in rules:
                print(f"{rule.id} | {rule.type} | {rule.category} | {rule.amount}원 | 매월 {rule.day}일 | 시작 {rule.start_month}")
            if not rules:
                print("반복 규칙 없음")
        elif args.recurring_command == "generate":
            service.generate_recurring(args.month)

    return 0

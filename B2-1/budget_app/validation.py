from datetime import datetime


# 날짜 형식 유효성 확인
def validate_date(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from error
    if parsed.strftime("%Y-%m-%d") != value:
        raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.")
    return value


# 날짜 형식 유효성 확인
def validate_month(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("월은 YYYY-MM 형식이어야 합니다.")
    try:
        parsed = datetime.strptime(value, "%Y-%m")
    except ValueError as error:
        raise ValueError("월은 YYYY-MM 형식이어야 합니다.") from error
    if parsed.strftime("%Y-%m") != value:
        raise ValueError("월은 YYYY-MM 형식이어야 합니다.")
    return value


# 금액 범위 확인
def positive_amount(amount: int) -> int:
    if type(amount) is not int or amount <= 0:
        raise ValueError("금액은 0보다 큰 정수여야 합니다.")
    return amount


# 수량(또는 옵션) 확인
def positive_count(count: int, name: str) -> int:
    if type(count) is not int or count <= 0:
        raise ValueError(f"{name}은 1 이상의 정수여야 합니다.")
    return count


# 날짜 범위 확인
def validate_period(start: str | None, end: str | None) -> None:
    if start is not None:
        validate_date(start)
    if end is not None:
        validate_date(end)
    if start and end and start > end:
        raise ValueError("--from은 --to보다 늦을 수 없습니다.")

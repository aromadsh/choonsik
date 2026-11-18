import functools
import sys
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def handle_exceptions(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except (ValueError, OSError, UnicodeError, KeyError, TypeError) as error:
            print(f"[오류] {error}", file=sys.stderr)
            print("[힌트] 입력값, 저장 경로와 파일 형식을 확인하세요.", file=sys.stderr)
            raise SystemExit(1) from None
        except (EOFError, KeyboardInterrupt):
            print("\n[오류] 입력이 중단되었습니다.", file=sys.stderr)
            print("[힌트] 명령어를 다시 실행하세요.", file=sys.stderr)
            raise SystemExit(1) from None
    return wrapper

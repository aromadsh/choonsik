import functools
import sys
import time
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

def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        print(f"[시작] {func.__qualname__}")
        try:
            result = func(*args, **kwargs)
        except Exception as error:
            elapsed = time.perf_counter() - start_time
            print(f"[실패] {func.__qualname__}")
            print(f"[오류] {type(error).__name__}: {error}")
            print(f"[실행 시간] {elapsed:.4f}초")
            raise  # 기존 handle_exceptions 등이 후속 처리하도록 전달
        else:
            elapsed = time.perf_counter() - start_time
            print(f"[완료] {func.__qualname__}")
            print(f"[실행 시간] {elapsed:.4f}초")
            return result

    return wrapper
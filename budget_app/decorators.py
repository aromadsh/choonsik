import functools
import sys
import time
from typing import Callable, Any

def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    예외 처리를 담당하는 데코레이터.
    스택트레이스 출력을 막고 원인과 해결 힌트를 출력한 뒤 비정상 종료(exit code != 0)합니다.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"[오류] 잘못된 입력값입니다: {e}", file=sys.stderr)
            print("[힌트] 입력 형식을 확인하고 다시 시도해주세요.", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"[오류] 파일을 찾을 수 없습니다: {e}", file=sys.stderr)
            print("[힌트] 초기화 작업이 정상적으로 수행되었는지 확인해주세요.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[오류] 예상치 못한 오류가 발생했습니다: {e}", file=sys.stderr)
            print("[힌트] 프로그램 실행 인자나 데이터를 확인해주세요.", file=sys.stderr)
            sys.exit(1)
    return wrapper

def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """함수 실행 시간을 측정하여 디버깅 로그로 남기는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        # 필요시 디버깅 용도로 활용 (현재는 패스 또는 로그 출력 가능)
        if elapsed >= 1.0:
            print(f"[성능 경고] '{func.__name__}' 작업이 2초를 초과했습니다. (소요 시간: {elapsed:.2f}초)")
        return result
    return wrapper
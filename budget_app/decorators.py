import sys
from functools import wraps

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"[오류] {e}")
            print(f"[힌트] 입력값이나 형식을 다시 확인해주세요.")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"[오류] 파일을 찾을 수 없습니다: {e}")
            print(f"[힌트] 저장 폴더 및 파일 경로를 확인해주세요.")
            sys.exit(1)
        except Exception as e:
            print(f"[오류] 예상치 못한 오류가 발생했습니다: {e}")
            print(f"[힌트] 명령어와 인자를 다시 확인해주세요.")
            sys.exit(1)
    return wrapper
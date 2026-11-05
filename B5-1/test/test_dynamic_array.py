import sys
from pathlib import Path

# 상위 폴더(mini-redis)의 모듈을 가져오기 위한 경로 설정
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dynamic_array import DynamicArray


def test_dynamic_array():
    array = DynamicArray(capacity=2)

    print("=== 동적 배열 테스트 ===")
    print(f"초기 배열 용량: {array.capacity}")
    print("-" * 55)

    # 1. append 및 자동 확장 테스트
    print("[1] append 및 용량 확장")

    for i in range(1, 10):
        value = f"value{i}"

        old_capacity = array.capacity
        array.append(value)

        print(
            f"데이터 {array.size():2d}개 | "
            f"배열 용량 {array.capacity:2d}개"
        )

        if array.capacity > old_capacity:
            print(
                f"  → 동적 배열 확장 발생! "
                f"{old_capacity} → {array.capacity}"
            )

    print("-" * 55)

    # 2. get 테스트
    print("[2] get 테스트")

    print(f"get(0): {array.get(0)}")
    print(f"get(4): {array.get(4)}")

    print("-" * 55)

    # 3. set 테스트
    print("[3] set 테스트")

    print(f"변경 전: {array.get(0)}")

    array.set(0, "updated")

    print(f"변경 후: {array.get(0)}")

    print("-" * 55)

    # 4. remove 테스트
    print("[4] remove 테스트")

    print(f"삭제 전 데이터 개수: {array.size()}")

    removed = array.remove(0)

    print(f"삭제된 데이터: {removed}")
    print(f"삭제 후 데이터 개수: {array.size()}")
    print(f"삭제 후 첫 번째 데이터: {array.get(0)}")

    print("-" * 55)

    # 5. 전체 데이터 확인
    print("[5] 전체 데이터 확인")

    for i in range(array.size()):
        print(f"index {i}: {array.get(i)}")

    print("=== 테스트 완료 ===")


if __name__ == "__main__":
    test_dynamic_array()
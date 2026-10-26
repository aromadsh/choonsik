import sys
from pathlib import Path

# 상위 폴더(mini-redis)의 모듈을 가져오기 위한 경로 설정
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hash_map import HashMap


def test_load_factor():
    hash_map = HashMap()

    print("=== 해시맵 로드 팩터 테스트 ===")
    print(f"초기 버킷 수: {hash_map.capacity}")
    print("-" * 55)

    for i in range(1, 18):
        key = f"key{i}"
        value = f"value{i}"

        # 키와 값 추가
        old_capacity = hash_map.capacity
        hash_map.put(key, value)

        # 현재 상태 확인
        count = hash_map.size()
        capacity = hash_map.capacity
        load_factor = count / capacity

        print(
            f"키 {count:2d}개 | "
            f"버킷 {capacity:2d}개 | "
            f"로드 팩터 {load_factor:.3f}"
        )

        # 버킷 확장 발생 여부 확인
        if capacity > old_capacity:
            print(
                f"  → 리해싱 발생! "
                f"버킷 {old_capacity}개 → {capacity}개"
            )

    print("-" * 55)
    print("=== 저장된 데이터 확인 ===")

    for i in range(1, 18):
        key = f"key{i}"
        value = hash_map.get(key)
        print(f"{key}: {value}")

    print("=== 테스트 완료 ===")


if __name__ == "__main__":
    test_load_factor()
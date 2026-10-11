from hash_map import HashMap


def test_basic_operations():
    """기본 저장, 조회, 삭제 테스트"""
    db = HashMap()

    db.put("user:1", "Alice")
    db.put("user:2", "Bob")

    assert db.get("user:1") == "Alice"
    assert db.get("user:2") == "Bob"
    assert db.get("unknown") is None

    assert db.contains("user:1") is True
    assert db.contains("unknown") is False
    assert db.size() == 2

    db.put("user:1", "Charlie")

    assert db.get("user:1") == "Charlie"
    assert db.size() == 2

    assert db.remove("user:1") == "Charlie"
    assert db.contains("user:1") is False
    assert db.size() == 1

    print("Basic operations TEST PASS")


def test_collision():
    """해시 충돌 처리 테스트"""
    db = HashMap(capacity=2)

    db.put("A", "Apple")
    db.put("C", "Cherry")

    # A와 C는 capacity=2에서 동일한 버킷에 배정된다.
    assert db.get("A") == "Apple"
    assert db.get("C") == "Cherry"

    assert db.remove("A") == "Apple"
    assert db.get("C") == "Cherry"

    print("Hash collision TEST PASS")


def test_resize():
    """로드 팩터에 따른 버킷 확장 테스트"""
    db = HashMap(capacity=4)

    assert db.capacity == 4

    db.put("key1", "value1")
    db.put("key2", "value2")
    db.put("key3", "value3")

    # 로드 팩터가 정확히 0.75면 확장하지 않는다.
    assert db.capacity == 4

    db.put("key4", "value4")

    assert db.capacity == 8
    assert db.size() == 4

    for i in range(1, 5):
        assert db.get(f"key{i}") == f"value{i}"

    print("Resize TEST PASS")


def test_keys():
    """전체 키 조회 테스트"""
    db = HashMap()

    db.put("name", "Alice")
    db.put("city", "Seoul")
    db.put("age", "30")

    keys = db.keys()

    assert keys.size() == 3

    for expected in ("name", "city", "age"):
        found = False

        for i in range(keys.size()):
            if keys.get(i) == expected:
                found = True
                break

        assert found

    print("Keys TEST PASS")


def test_edge_cases():
    """빈 해시맵, None 값, 한글 키 테스트"""
    db = HashMap()

    assert db.size() == 0
    assert db.keys().size() == 0
    assert db.remove("missing") is None

    db.put("empty", None)

    assert db.contains("empty") is True
    assert db.get("empty") is None

    db.put("사용자:1", "홍길동")

    assert db.get("사용자:1") == "홍길동"

    print("Edge cases TEST PASS")


if __name__ == "__main__":
    test_basic_operations()
    test_collision()
    test_resize()
    test_keys()
    test_edge_cases()

    print("STEP 2 ALL TESTS PASS")
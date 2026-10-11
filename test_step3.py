from min_heap import MinHeap
from mini_redis import MiniRedis


def test_heap():
    """최소 힙 정렬 테스트"""
    heap = MinHeap()

    assert heap.peek() is None
    assert heap.pop() is None

    items = [
        (30, 1, "C"),
        (10, 2, "A"),
        (20, 3, "B"),
        (5, 4, "D"),
    ]

    for item in items:
        heap.push(item)

    assert heap.peek() == (5, 4, "D")

    result = [heap.pop()[0] for _ in range(4)]

    assert result == [5, 10, 20, 30]
    assert heap.size() == 0

    print("MinHeap TEST PASS")


def test_ttl():
    """TTL 설정 및 만료 테스트"""
    now = [1000.0]
    db = MiniRedis(clock=lambda: now[0])

    assert db.set("user:1", "Alice") == "OK"
    assert db.ttl("user:1") == -1
    assert db.ttl("missing") == -2

    assert db.expire("missing", 3) == 0
    assert db.expire("user:1", 3) == 1
    assert db.ttl("user:1") == 3

    now[0] += 1
    assert db.ttl("user:1") == 2

    now[0] += 2

    assert db.get("user:1") is None
    assert db.ttl("user:1") == -2
    assert db.dbsize() == 0

    print("TTL TEST PASS")


def test_stale_events():
    """오래된 TTL 이벤트 무시 테스트"""
    now = [1000.0]
    db = MiniRedis(clock=lambda: now[0])

    db.set("x", "old")
    db.expire("x", 2)
    db.expire("x", 10)

    now[0] = 1003

    assert db.get("x") == "old"
    assert db.dbsize() == 1

    db.set("x", "new")

    assert db.ttl("x") == -1

    now[0] = 1011

    assert db.dbsize() == 1
    assert db.get("x") == "new"

    assert db.delete("x") == 1
    assert db.delete("x") == 0

    db.set("x", "again")

    assert db.expire("x", 0) == 1
    assert db.exists("x") == 0

    print("Lazy deletion TEST PASS")


def test_keys_expire():
    """KEYS, DBSIZE 만료 처리 테스트"""
    now = [0.0]
    db = MiniRedis(clock=lambda: now[0])

    db.set("a", "A")
    db.set("b", "B")
    db.expire("a", 2)

    now[0] = 3.0

    assert db.dbsize() == 1

    keys = db.keys()

    assert keys.size() == 1
    assert keys.get(0) == "b"

    print("DBSIZE/KEYS TEST PASS")


if __name__ == "__main__":
    test_heap()
    test_ttl()
    test_stale_events()
    test_keys_expire()

    print("STEP 3 ALL TESTS PASS")
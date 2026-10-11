from cli import execute
from mini_redis import MiniRedis, OOM_ERROR


def test_lru_memory():
    """LRU 제거 및 메모리 사용량 테스트."""
    db = MiniRedis()

    assert db.config_set_maxmemory(30) == "OK"

    assert db.set("user:1", "Alice") == "OK"
    assert db.set("user:2", "Bob") == "OK"
    assert db.set("user:3", "Charlie") == "OK"

    assert db.get("user:1") is None
    assert db.used_memory == 22
    assert db.evicted_keys == 1

    assert db.get("user:2") == "Bob"

    assert db.set(
        "x", "12345678901234567890"
    ) == "OK"

    assert db.evicted_keys == 2
    assert db.get("user:3") is None
    assert db.get("x") == "12345678901234567890"

    print("LRU memory TEST PASS")


def test_oom_overwrite_unicode():
    """OOM, 덮어쓰기, UTF-8 테스트."""
    db = MiniRedis()

    db.config_set_maxmemory(9)

    assert db.set("한", "가") == "OK"
    assert db.used_memory == 6

    assert db.set(
        "한", "very-long-value"
    ) == OOM_ERROR

    assert db.get("한") == "가"
    assert db.used_memory == 6

    assert db.set("한", "나") == "OK"
    assert db.used_memory == 6

    assert db.set("a", "b") == "OK"
    assert db.used_memory == 8

    assert db.config_set_maxmemory(4) == "OK"

    assert db.exists("한") == 0
    assert db.exists("a") == 1
    assert db.evicted_keys == 1

    assert db.config_set_maxmemory(0) == "OK"
    assert db.set("huge", "x" * 100) == "OK"

    print("OOM, overwrite, UTF-8 TEST PASS")


def test_expire_lru():
    """TTL과 LRU의 연동 테스트."""
    now = [1000.0]

    db = MiniRedis(clock=lambda: now[0])
    db.config_set_maxmemory(20)

    db.set("a", "12345")
    db.set("b", "12345")

    db.expire("a", 2)

    now[0] = 1003

    assert db.get("a") is None
    assert db.used_memory == 6
    assert db.dbsize() == 1

    assert db.set("a", "new") == "OK"
    assert db.ttl("a") == -1

    assert db.delete("b") == 1
    assert db.used_memory == 4
    assert db.keys().size() == 1

    print("TTL + LRU TEST PASS")


def test_cli():
    """CLI 명령어와 오류 처리 테스트."""
    db = MiniRedis()

    assert execute(
        db, "CONFIG SET maxmemory abc"
    ) == "(error) ERR value is not an integer or out of range"

    assert execute(
        db, "CONFIG SET maxmemory 40"
    ) == "OK"

    assert execute(
        db, 'SET greeting "Hello World"'
    ) == "OK"

    assert execute(
        db, "GET greeting"
    ) == '"Hello World"'

    assert execute(
        db, "EXISTS greeting"
    ) == "(integer) 1"

    assert execute(
        db, "TTL greeting"
    ) == "(integer) -1"

    assert execute(
        db, "DBSIZE"
    ) == "(integer) 1"

    assert execute(
        db, "EXPIRE greeting -1"
    ) == "(integer) 1"

    assert execute(
        db, "GET greeting"
    ) == "(nil)"

    assert execute(
        db, "KEYS"
    ) == "(empty array)"

    assert execute(
        db, "GET"
    ) == "(error) ERR wrong number of arguments for 'GET' command"

    assert execute(
        db, "HELLO"
    ) == "(error) ERR unknown command 'HELLO'"

    assert "used_memory:0" in execute(
        db, "INFO memory"
    )

    print("CLI TEST PASS")


if __name__ == "__main__":
    test_lru_memory()
    test_oom_overwrite_unicode()
    test_expire_lru()
    test_cli()

    print("STEP 4 ALL TESTS PASS")
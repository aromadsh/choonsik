import time

from hash_map import HashMap
from min_heap import MinHeap
from doubly_linked_list import DoublyLinkedList

OOM_ERROR = (
    "(error) OOM command not allowed"
    "when used_memory > 'maxmemory'"
)

class RedisEntry:
    # 문자열 값, 만료 시각, 만료 이벤트 버전
    # 문자열 값과 TTL, LRU 메타데이터

    def __init__(self, value):
        self.value = value
        self.expire_at = None
        self.version = 0
        self.lru_node = None


class MiniRedis:
    #  해시맵과 최조 힙을 결합한 TTL 저장소

    def __init__(self, clock=None):
        self.data = HashMap()
        self.expirations = MinHeap()
        self.lru = DoublyLinkedList()

        self.clock = clock if clock is not None else time.time
        self.next_version = 0

        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    # 키를 삭제, 힙 이벤트는 지연 삭제 (이전 코드)
    #     def _delete_key(self, key):
    #         if not self.data.contains(key):
    #             return False

    #         self.data.remove(key)
    #         return True
    # 해시맵, LRU, 메모리 사용량을 함게 갱신
    def _delete_key(self, key):
        entry = self.data.get(key)

        if entry is None:
            return False

        self.used_memory -= self._entry_size(key, entry.value)

        self.lru.remove_node(entry.lru_node)
        self.data.remove(key)

        return True

    # 특정 키의 만료 여부를 확인
    def _expire_if_needed(self, key):
        entry = self.data.get(key)

        if entry is None:
            return False

        if (entry.expire_at is not None) and (entry.expire_at <= self.clock()):
            self._delete_key(key)
            return True

        return False

    # 힙에서 유효한 만료 이벤트를 찾아 키를 삭제
    def _purge_expired(self):
        now = self.clock()

        while (self.expirations.size()) and (self.expirations.peek()[0] <= now):
            expire_at, version, key = self.expirations.pop()

            entry = self.data.get(key)

            if (entry is not None) and (entry.version == version) and (entry.expire_at == expire_at):
                self._delete_key(key)

    # SET: 키와 값을 저장하고 기존 TTL을 초기화 (이전 코드)
    # def set(self, key, value):
    #     self._expire_if_needed(key)

    #     self.data.put(key, RedisEntry(value))

    #     return "OK"
    # SET: TTL 초기화, LRU 갱신, 메모리 제한 처리
    def set(self, key, value):
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("Key and value must be strings")

        self._purge_expired()

        new_size = self._entry_size(key, value)

        if (self.maxmemory > 0) and (new_size > self.maxmemory):
            return OOM_ERROR

        entry = self.data.get(key)

        if entry is None:
            entry = RedisEntry(value)
            entry.lru_node = self.lru.insert_front(key)

            self.data.put(key, entry)
            self.used_memory += new_size

        else:
            self.used_memory -= self._entry_size(key, entry.value)

            entry.value = value
            entry.expire_at = None
            entry.version = 0

            self.used_memory += new_size

            self.lru.move_to_front(entry.lru_node)

        self._evict_to_limit()

        return "OK"

    # GET: 만료되지 않은 키의 값을 반환 (이전 코드)
    # def get(self, key):
    #     self._expire_if_needed(key)

    #     entry = self.data.get(key)

    #     if entry is None:
    #         return None

    #     return entry.value
    # GET: 성공한 조회만 LRU를 갱신
    def get(self, key):
        self._expire_if_needed(key)

        entry = self.data.get(key)

        if entry is None:
            return None

        self.lru.move_to_front(entry.lru_node)

        return entry.value

    # DEL: 키를 삭제
    def delete(self, key):
        self._expire_if_needed(key)

        if self._delete_key(key):
            return 1

        return 0

    # EXISTS: 키가 존재하면 1을 반환
    def exists(self, key):
        self._expire_if_needed(key)

        if self.data.contains(key):
            return 1

        return 0

    # DBSIZE: 만료된 키를 정리한 후 개수를 반환
    def dbsize(self):
        self._purge_expired()

        return self.data.size()

    # KEY: 만료되지 않은 모든 키를 반환
    def keys(self):
        self._purge_expired()

        return self.data.keys()

    # EXPIRE: 키의 만료 시간을 설정
    def expire(self, key, seconds):
        self._expire_if_needed(key)

        entry = self.data.get(key)

        if entry is None:
            return 0

        if seconds <= 0:
            self._delete_key(key)
            return 1

        self.next_version += 1

        entry.version = self.next_version
        entry.expire_at = self.clock() + seconds

        self.expirations.push((entry.expire_at, entry.version, key))

        return 1

    # TTL: 키의 남은 만료 시간을 초 단위로 반환
    def ttl(self, key):
        self._expire_if_needed(key)

        entry = self.data.get(key)

        if entry is None:
            return -2

        if entry.expire_at is None:
            return -1

        remaining = entry.expire_at - self.clock()

        if remaining <= 0:
            self._delete_key(key)
            return -2

        return int(remaining)

    # UTF-8 기준 엔트리의 크기를 계산
    def _entry_size(self, key, value):
        return (len(key.encode("utf-8")) + len(value.encode("utf-8")))

    # 메모리가 제한 이하가 될 때까지 LRU 키를 제거
    def _evict_to_limit(self):
        if self.maxmemory == 0:
            return

        while self.used_memory > self.maxmemory:
            tail = self.lru.tail

            if tail is None:
                break

            self._delete_key(tail.data)
            self.evicted_keys += 1

    # 최대 메모리를 설정
    def config_set_maxmemory(self, number):
        if (not isinstance(number, int)) or (number < 0):
            raise ValueError("maxmemory must be nonnegative integer")

        self._purge_expired()
        self.maxmemory = number
        self._evict_to_limit()

        return "OK"

    # 현재 메모리 상태를 반환
    def info_memory(self):
        self._purge_expired()

        return (
            f"used_memory:{self.used_memory}\n"
            f"maxmemory:{self.maxmemory}\n"
            f"evicted_keys:{self.evicted_keys}"
        )


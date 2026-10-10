from dynamic_array import DynamicArray
from doubly_linked_list import DoublyLinkedList

class HashEntry:
    # 해시맵에 저장하는 키와 값

    def __init__(self, key, value):
        self.key = key
        self.value = value

class HashMap:
    # 체이닝 방식으로 구현한 해시맵

    def __init__(self, capacity=8):
        if capacity < 1:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        self.count = 0
        self.load_factor_limit = 0.75

        self.buckets = self._create_buckets(capacity)

    # 버킷 배열 생성
    def _create_buckets(self, capacity):
        buckets = DynamicArray(capacity)

        for _ in range(capacity):
            buckets.append(DoublyLinkedList())

        return buckets

    # 문자열을 해시 인덱스로 변환
    def _hash(self, key):
        if not isinstance(key, str):
            raise TypeError("key must be a string")

        hash_value = 0

        for byte in key.encode("utf-8"):
            hash_value = (hash_value * 31 + byte) % self.capacity

        return hash_value

    # 키가 저장된 노드 검색
    def _find_node(self, key):
        index = self._hash(key)
        bucket = self.buckets.get(index)

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                return current

            current = current.next

        return None

    # 새 엔트리를 삽입하거나 기존 값을 수정
    def put(self, key, value):
        node = self._find_node(key)

        if node is not None:
            node.data.value = value
            return

        index = self._hash(key)
        bucket = self.buckets.get(index)

        bucket.insert_back(HashEntry(key, value))
        self.count += 1

        if self.count / self.capacity > self.load_factor_limit:
            self._resize()

    # 키로 값 조회
    def get(self, key):
        node = self._find_node(key)

        if node is None:
            return None

        return node.data.value

    # 키에 해당하는 엔트리 삭제
    def remove(self, key):
        index = self._hash(key)
        bucket = self.buckets.get(index)

        current = bucket.head

        while current is not None:
            if current.data.key == key:
                removed_value = current.data.value
                bucket.remove_node(current)
                self.count -= 1
                return removed_value

            current = current.next

        return None

    # 키 존재 여부 반환
    def contains(self, key):
        return self._find_node(key) is not None

    # 모든 키를 목록으로 반환
    def keys(self):
        result = DynamicArray()

        for i in range(self.capacity):
            bucket = self.buckets.get()
            current = bucket.head

            while current is not None:
                result.append(current.data.key)
                current = current.next

        return result

    # 저장된 엔트리 개수 반환
    def size(self):
        return self.count

    # 버킷 수를 2배로 확장하고 재배치
    def _resize(self):
        old_buckets = self.buckets
        old_capacity = self.capacity

        self.capacity *= 2
        self.buckets = self._create_buckets(self.capacity)

        for i in range(old_capacity):
            bucket = old_buckets.get(i)
            current = bucket.head

            while current is not None:
                entry = current.data

                new_index = self._hash(entry.key)
                new_bucket = self.buckets.get(new_index)

                new_bucket.insert_back(entry)
                current = current.next

            
            


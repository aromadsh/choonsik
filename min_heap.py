from dynamic_array import DynamicArray

class MinHeap:
    # 튜플을 정렬하는 최소 힙 (expire_at, version, key)

    def __init__(self):
        self.items = DynamicArray()

    def size(self):
        return self.items.size()

    # 가장 작은 항목을 조회
    def peek(self):
        if self.size() == 0:
            return None

        return self.items.get(0)

    # 항목을 추가하고 힙 속성을 복원
    def push(self, item):
        self.items.append(item)
        self._heapify_up(self.size() - 1)

    # 가장 작은 항목ㅇ을 제거하고 반환
    def pop (self):
        if self.size() == 0:
            return None

        root = self.items.get(0)
        last = self.items.remove(self.size() - 1)

        if self.size() > 0:
            self.items.set(0, last)
            self._heapify_down(0)

        return root

    # 두 인덱스의 값을 교환
    def _swap(self, i, j):
        left = self.items.get(i)
        right = self.items.get(j)

        self.items.set(i, right)
        self.items.set(j, left)

    # 삽입된 항목을 부모와 비교하며 위로 이동
    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.items.get(parent) <= self.items.get(index):
                break

            self._swap(parent, index)
            index = parent

    # 루트 항목을 자식과 비교하며 아래로 이동
    def _heapify_down(self, index):
        while True:
            left = index * 2 + 1
            right = left + 1
            smallest = index

            if (left < self.size()) and (self.items.get(left) < self.items.get(smallest)):
                smallest = left

            if (right < self.size()) and (self.items.get(right) < self.items.get(smallest)):
                smallest = right

            if smallest == index:
                break

            self._swap(index, smallest)
            index = smallest

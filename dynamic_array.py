class DynamicArray:
    """용량을 자동 확장하는 동적 배열"""

    def __init__(self, capacity=2):
        if capacity < 1:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        self.length = 0
        self.data = [None] * capacity

    def size(self):
        return self.length
    

    """기존 용량을 2배로 확장"""
    def _resize(self): 
        new_capacity = self.capacity * 2
        new_data = [None] * new_capacity

        for i in range(self.length):
            new_data[i] = self.data[i]

        self.data = new_data
        self.capacity = new_capacity


    """배열 끝에 데이터를 추가"""
    def append(self, value):
        if self.length == self.capacity:
            self._resize()
                                                                                       
        self.data[self.length] = value
        self.length += 1


    """인덱스에 해당하는 값을 조회"""
    def get(self, index):
        if (index < 0) or (index >= self.length):
            raise IndexError("index out of range")

        return self.data[index]


    """인덱스에 해당하는 값 수정"""
    def set(self, index, value):
        if index < 0 or index >= self.length:
            raise IndexError("index out of range")

        self.data[index] = value


    """특정 위치의 데이터를 삭제"""
    def remove(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("index out of range")

        removed = self.data[index]

        for i in range(index, self.length - 1):
            self.data[i] = self.data[i + 1]

        self.length -= 1
        self.data[self.length] = None

        return removed

    def __len__(self):
        return self.length
    

    
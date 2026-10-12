from doubly_linked_list import DoublyLinkedList

class Stack:
    # LIFO: push/pop 모두 0(1)

    def __init__(self):
        self.items = DoublyLinkedList()

    def push(self, value):
        self.items.insert_back(value)

    def pop(self):
        node = self.items.remove_back()
        return None if node is None else node.data

    def peek(self):
        return (None if self.items.tail is None else self.items.tail.data)

    def size(self):
        return self.items.size()


class Queue:
    # FIFO: enqueue/dequeue 모두 0(1)

    def __init__(self):
        self.items = DoublyLinkedList()

    def enqueue(self, value):
        self.items.insert_back(value)

    def dequeue(self):
        node = self.items.remove_front()
        return None if node is None else node.data

    def peek(self):
        return (None if self.items.head is None else self.items.head.data)

    def size (self):
        return self.items.size()


class Deque:
    # 양쪽 끝에 삽입과 삭제가 가능한 자료구조

    def __init__(self):
        self.items = DoublyLinkedList()

    def append_left(self, value):
        self.items.insert_front(value)

    def append_right(self, value):
        self.items.insert_back(value)

    def pop_left(self):
        node = self.items.remove_front()
        return None if node is None else node.data

    def pop_right(self):
        node = self.items.remove_back()
        return None if node is None else node.data

    def size(self):
        return self.items.size()

    
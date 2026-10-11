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

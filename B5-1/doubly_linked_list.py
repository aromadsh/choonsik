class Node:
    # 이중 연결 리스트의 노드

    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    # 양방향 탐색이 가능한 연결 리스트

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def size(self):
        return self.length


    # 맨 앞에 노드를 추가
    def insert_front(self, data):
        node = Node(data)

        node.next = self.head

        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node
        self.length += 1

        return node

    # 맨 뒤에 노드를 추가
    def insert_back(self, data):
        node = Node(data)

        node.prev = self.tail

        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node

        self.tail = node
        self.length += 1

        return node

    # 맨 앞 노드를 제거
    def remove_front(self):
        if self.head is None:
            return None

        return self.remove_node(self.head)

    # 맨 뒤 노드를 제거
    def remove_back(self):
        if self.tail is None:
            return None

        return self.remove_node(self.tail)

    # 이미 참조하고 있는 노드 제거
    def remove_node(self, node):
        if node is None:
            return None

        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        self.length -= 1

        node.prev = None
        node.next = None

        return node

    # 기존 노드를 맨 앞으로 이동
    def move_to_front(self, node):
        if node is None or node is self.head:
            return

        if node.prev is not None:
            node.prev.next = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = self.head

        self.head.prev = node
        self.head = node

        def __len__(self):
            return self.length
    
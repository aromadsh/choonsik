from dynamic_array import DynamicArray


class BSTNode:
    # 왼쪽에는 작은 값, 오른쪽에는 큰 값을 저장

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    # 삽입, 검색, 삭제 및 중위 순회를 지원하는 BST

    def __init__(self):
        self.root = None
        self.count = 0

    # 중복 값은 삽입하지 않음
    def insert(self, value):

        def visit(node):
            if node is None:
                return BSTNode(value), True

            if value < node.value:
                node.left, added = visit(node.left)
            elif value > node.value:
                node.right, added = visit(node.right)
            else:
                return node, False

            return node, added

        self.root, added = visit(self.root)

        if added:
            self.count += 1

        return added

    # 값을 비교하며 왼쪽 또는 오른쪽으로 탐색
    def search(self, value):
        node = self.root

        while node is not None:
            if value == node.value:
                return True

            node = (node.left if value < node.value else node.right)

        return False

    # 자식 수에 따라 노드를 삭제
    def delete(self, value):

        def remove(node, target):
            if node is None:
                return None, False

            if target < node.value:
                node.left, deleted = remove(node.left, target)
                return node, deleted

            if target > node.value:
                node.right, deleted = remove(node.right, target)
                return node, deleted

            if node.left is None:
                return node.right, True

            if node.right is None:
                return node.left, True

            successor = node.right

            while successor.left is not None:
                successor = successor.left

            node.value = successor.value

            node.right, _ = remove(node.right, successor.value)

            return node, True

        self.root, deleted = remove(self.root, value)

        if deleted:
            self.count -= 1

        return deleted

    # 중위 순회로 정렬된 값을 반환
    def inorder(self):
        result = DynamicArray()

        def visit(node):
            if node is None:
                return

            visit(node.left)
            result.append(node.value)
            visit(node.right)

        visit(self.root)
        return result

    def size(self):
        return self.count
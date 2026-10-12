from dynamic_array import DynamicArray
from stack_queue_deque import Queue


class TreeNode:
    # 일반 이진 트리 노드

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    # 전위, 중위, 후위, 레벨 순회 제공

    def __init__(self, root=None):
        self.root = root

    def preorder(self):
        result = DynamicArray()

        def visit(node):
            if node is None:
                return

            result.append(node.value)
            visit(node.left)
            visit(node.right)

        visit(self.root)
        return result

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

    def postorder(self):
        result = DynamicArray()

        def visit(node):
            if node is None:
                return

            visit(node.left)
            visit(node.right)
            result.append(node.value)

        visit(self.root)
        return result

    def levelorder(self):
        result = DynamicArray()

        if self.root is None:
            return result

        queue = Queue()
        queue.enqueue(self.root)

        while queue.size():
            node = queue.dequeue()
            result.append(node.value)

            if node.left is not None:
                queue.enqueue(node.left)

            if node.right is not None:
                queue.enqueue(node.right)

        return result
    
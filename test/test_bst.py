import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bst import BinarySearchTree


# BST 생성
bst = BinarySearchTree()


# 1. 삽입
print("=== 1. 삽입 ===")

for value in [50, 30, 70, 20, 40, 60, 80]:
    bst.insert(value)
    print(f"{value} 삽입")


# 2. 중위 순회
print("\n=== 2. 중위 순회 ===")

result = bst.inorder()
print([result.get(i) for i in range(result.size())])


# 3. 탐색
print("\n=== 3. 탐색 ===")

print("40 탐색:", bst.search(40))
print("90 탐색:", bst.search(90))


# 4. 삭제
print("\n=== 4. 삭제 ===")

bst.delete(30)
print("30 삭제 완료")


# 5. 삭제 후 중위 순회
print("\n=== 5. 삭제 후 중위 순회 ===")

result = bst.inorder()
print([result.get(i) for i in range(result.size())])
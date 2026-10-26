import sys
from pathlib import Path

# 상위 폴더의 기존 자료구조 가져오기
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stack_queue_deque import Stack, Queue, Deque


# ==========================================
# 1. 현재 데이터 확인
# ==========================================

def show_items(collection):
    """
    기존 DoublyLinkedList의 head부터 tail까지
    순회하여 현재 저장된 값을 출력합니다.
    """

    values = []
    node = collection.items.head

    while node is not None:
        values.append(node.data)
        node = node.next

    print(f"\n현재 데이터: {values}")
    print(f"데이터 개수: {collection.size()}")


# ==========================================
# 2. 초기 데이터 입력
# ==========================================

def input_initial_values(collection, kind):
    """
    쉼표로 구분된 데이터를 입력받아
    선택한 자료구조에 추가합니다.
    """

    raw = input(
        "\n초기 데이터를 입력하세요 "
        "(예: A,B,C 또는 10,20,30 / Enter는 건너뛰기): "
    ).strip()

    if not raw:
        return

    values = [
        value.strip()
        for value in raw.split(",")
        if value.strip()
    ]

    for value in values:
        if kind == "stack":
            collection.push(value)

        elif kind == "queue":
            collection.enqueue(value)

        elif kind == "deque":
            collection.append_right(value)

    print("\n초기 데이터 입력 완료!")
    show_items(collection)


# ==========================================
# 3. Stack 테스트
# ==========================================

def test_stack():
    stack = Stack()

    print("\n========== STACK ==========")
    print("LIFO: 마지막에 들어온 데이터가 먼저 나옵니다.")

    input_initial_values(stack, "stack")

    while True:
        print("\n[Stack 메뉴]")
        print("1. push - 데이터 추가")
        print("2. pop  - 데이터 삭제")
        print("3. peek - 마지막 데이터 확인")
        print("4. 현재 데이터 확인")
        print("0. 메인 메뉴")

        choice = input("선택: ").strip()

        if choice == "1":
            value = input("추가할 값: ")
            stack.push(value)

            print(f"추가: {value}")
            show_items(stack)

        elif choice == "2":
            if stack.size() == 0:
                print("Stack이 비어 있습니다.")
            else:
                value = stack.pop()
                print(f"삭제: {value}")

            show_items(stack)

        elif choice == "3":
            if stack.size() == 0:
                print("Stack이 비어 있습니다.")
            else:
                print(f"peek: {stack.peek()}")

        elif choice == "4":
            show_items(stack)

        elif choice == "0":
            break

        else:
            print("올바른 번호를 입력하세요.")


# ==========================================
# 4. Queue 테스트
# ==========================================

def test_queue():
    queue = Queue()

    print("\n========== QUEUE ==========")
    print("FIFO: 먼저 들어온 데이터가 먼저 나옵니다.")

    input_initial_values(queue, "queue")

    while True:
        print("\n[Queue 메뉴]")
        print("1. enqueue - 데이터 추가")
        print("2. dequeue - 데이터 삭제")
        print("3. peek    - 첫 번째 데이터 확인")
        print("4. 현재 데이터 확인")
        print("0. 메인 메뉴")

        choice = input("선택: ").strip()

        if choice == "1":
            value = input("추가할 값: ")
            queue.enqueue(value)

            print(f"추가: {value}")
            show_items(queue)

        elif choice == "2":
            if queue.size() == 0:
                print("Queue가 비어 있습니다.")
            else:
                value = queue.dequeue()
                print(f"삭제: {value}")

            show_items(queue)

        elif choice == "3":
            if queue.size() == 0:
                print("Queue가 비어 있습니다.")
            else:
                print(f"peek: {queue.peek()}")

        elif choice == "4":
            show_items(queue)

        elif choice == "0":
            break

        else:
            print("올바른 번호를 입력하세요.")


# ==========================================
# 5. Deque 테스트
# ==========================================

def test_deque():
    deque = Deque()

    print("\n========== DEQUE ==========")
    print("양쪽 끝에서 데이터 추가 및 삭제가 가능합니다.")

    input_initial_values(deque, "deque")

    while True:
        print("\n[Deque 메뉴]")
        print("1. append_left  - 왼쪽에 추가")
        print("2. append_right - 오른쪽에 추가")
        print("3. pop_left     - 왼쪽에서 삭제")
        print("4. pop_right    - 오른쪽에서 삭제")
        print("5. 현재 데이터 확인")
        print("0. 메인 메뉴")

        choice = input("선택: ").strip()

        if choice == "1":
            value = input("추가할 값: ")
            deque.append_left(value)

            print(f"왼쪽 추가: {value}")
            show_items(deque)

        elif choice == "2":
            value = input("추가할 값: ")
            deque.append_right(value)

            print(f"오른쪽 추가: {value}")
            show_items(deque)

        elif choice == "3":
            if deque.size() == 0:
                print("Deque가 비어 있습니다.")
            else:
                value = deque.pop_left()
                print(f"왼쪽 삭제: {value}")

            show_items(deque)

        elif choice == "4":
            if deque.size() == 0:
                print("Deque가 비어 있습니다.")
            else:
                value = deque.pop_right()
                print(f"오른쪽 삭제: {value}")

            show_items(deque)

        elif choice == "5":
            show_items(deque)

        elif choice == "0":
            break

        else:
            print("올바른 번호를 입력하세요.")


# ==========================================
# 6. 메인 메뉴
# ==========================================

def main():
    while True:
        print("\n" + "=" * 45)
        print("Mini Redis - 자료구조 대화형 테스트")
        print("=" * 45)
        print("1. Stack 테스트")
        print("2. Queue 테스트")
        print("3. Deque 테스트")
        print("0. 종료")

        choice = input("\n선택: ").strip()

        if choice == "1":
            test_stack()

        elif choice == "2":
            test_queue()

        elif choice == "3":
            test_deque()

        elif choice == "0":
            print("테스트를 종료합니다.")
            break

        else:
            print("올바른 번호를 입력하세요.")


if __name__ == "__main__":
    main()
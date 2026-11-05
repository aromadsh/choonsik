# Stack · Queue · Deque 학습 및 구현 문서

> **Mini Redis 보너스 과제 2** — 스택, 큐, 덱의 개념을 이해하고 기존 `DoublyLinkedList`를 재사용하는 구현과 활용 사례를 정리합니다.
>
> 이 문서는 `stack_queue_deque.py`, `doubly_linked_list.py`, `binary_tree.py`, `pubsub.py`, `test_step5.py`의 실제 구현을 기준으로 작성했습니다.

## 1. 먼저 알아둘 용어

- **자료구조(Data Structure):** 데이터를 저장하고 접근하는 방식입니다.
- **LIFO(Last In, First Out):** 마지막에 들어온 데이터가 먼저 나옵니다.
- **FIFO(First In, First Out):** 먼저 들어온 데이터가 먼저 나옵니다.
- **Head / Tail:** 이중 연결 리스트의 첫 번째 노드와 마지막 노드입니다.
- **`None`:** 현재 구현에서는 비어 있는 Stack/Queue/Deque에 대해 읽기·삭제를 시도했을 때 사용하는 반환값입니다. 따라서 실제로 `None`을 데이터로 저장한다면 빈 상태와 구분하기 어렵다는 점은 한계입니다.

## 2. 한눈에 비교

| 구분 | Stack (스택) | Queue (큐) | Deque (덱) |
|---|---|---|---|
| 동작 원칙 | **LIFO** — 후입선출 | **FIFO** — 선입선출 | 양쪽 끝에서 삽입·삭제 |
| 추가 | `push(value)` | `enqueue(value)` | `append_left(value)`, `append_right(value)` |
| 삭제 | `pop()` | `dequeue()` | `pop_left()`, `pop_right()` |
| 다음 값 확인 | `peek()` — 마지막 값 | `peek()` — 첫 값 | 현재 구현에는 별도 `peek` 없음 |
| 내부 저장 구조 | `DoublyLinkedList` | `DoublyLinkedList` | `DoublyLinkedList` |
| 주요 활용 | 되돌리기, DFS, 함수 호출 스택 | BFS, 레벨 순회, 메시지 버퍼 | 양방향 작업 큐, 슬라이딩 윈도 |
| **현재 프로젝트 실제 사용** | 독립 구현 및 테스트 | **`binary_tree.py`, `pubsub.py`** | 독립 구현 및 테스트 |

모든 자료구조는 **기존에 직접 구현한 이중 연결 리스트**를 재사용합니다. Python 내장 `list`나 `collections.deque`로 대체하지 않았습니다.

## 3. 왜 이중 연결 리스트를 재사용하나요?

이중 연결 리스트는 노드마다 `data`, `prev`, `next`를 갖고, 리스트 자체는 `head`와 `tail`을 기억합니다.

```text
HEAD                                       TAIL
  ↓                                         ↓
 [A]  <---->  [B]  <---->  [C]
```

`doubly_linked_list.py`의 핵심 메서드:

| 메서드 | 의미 | 시간 복잡도 |
|---|---|---|
| `insert_front(value)` | Head에 삽입 | O(1) |
| `insert_back(value)` | Tail에 삽입 | O(1) |
| `remove_front()` | Head 삭제, 노드 반환 | O(1) |
| `remove_back()` | Tail 삭제, 노드 반환 | O(1) |
| `size()` | 데이터 개수 확인 | O(1) |

양 끝을 탐색할 필요 없이 `head`와 `tail`을 바로 참조하기 때문에 O(1)입니다. **덱과 이중 연결 리스트는 동일한 개념이 아닙니다.** 덱은 *양쪽 끝에서 삽입·삭제한다는 동작 규칙*이고, 이중 연결 리스트는 그 동작을 지원하는 *내부 구현 방식*입니다. 덱은 원형 배열로도 구현할 수 있습니다.

## 4. Stack — 후입선출(LIFO)

### 4.1 동작 원리

```text
push(A)  → [A]
push(B)  → [A, B]
push(C)  → [A, B, C]  ← Top
pop()    → C 반환, [A, B]
pop()    → B 반환, [A]
```

마지막에 추가한 **C가 먼저 삭제**됩니다.

### 4.2 실제 코드: `stack_queue_deque.py`

```python
class Stack:
    def __init__(self):
        self.items = DoublyLinkedList()

    def push(self, value):
        self.items.insert_back(value)

    def pop(self):
        node = self.items.remove_back()
        return None if node is None else node.data

    def peek(self):
        return None if self.items.tail is None else self.items.tail.data

    def size(self):
        return self.items.size()
```

- `push`: Tail에 노드 추가, O(1).
- `pop`: Tail 노드 제거, O(1).
- `peek`: Tail 값만 확인하고 제거하지 않음, O(1).
- `size`: 저장된 노드 개수 반환, O(1).

### 4.3 직접 실행

```python
from stack_queue_deque import Stack

stack = Stack()
stack.push("A")
stack.push("B")
stack.push("C")
print(stack.peek())  # C
print(stack.pop())   # C
print(stack.pop())   # B
print(stack.pop())   # A
print(stack.pop())   # None
```

**과제 적용 여부:** 현재 `Stack` 클래스는 직접 구현 및 `test_step5.py` 검증용입니다. Mini Redis의 기본 명령어, TTL, LRU가 `Stack` 클래스를 직접 호출하는 것은 아닙니다.

## 5. Queue — 선입선출(FIFO)

### 5.1 동작 원리

```text
enqueue(A) → [A]
enqueue(B) → [A, B]
enqueue(C) → [A, B, C]
dequeue()  → A 반환, [B, C]
dequeue()  → B 반환, [C]
```

먼저 추가한 **A가 먼저 삭제**됩니다.

### 5.2 실제 코드: `stack_queue_deque.py`

```python
class Queue:
    def __init__(self):
        self.items = DoublyLinkedList()

    def enqueue(self, value):
        self.items.insert_back(value)

    def dequeue(self):
        node = self.items.remove_front()
        return None if node is None else node.data

    def peek(self):
        return None if self.items.head is None else self.items.head.data

    def size(self):
        return self.items.size()
```

- `enqueue`: Tail에 추가, O(1).
- `dequeue`: Head에서 제거, O(1).
- `peek`: Head 값만 확인, O(1).
- `size`: 데이터 개수, O(1).

### 5.3 직접 실행

```python
from stack_queue_deque import Queue

queue = Queue()
queue.enqueue("A")
queue.enqueue("B")
queue.enqueue("C")
print(queue.peek())     # A
print(queue.dequeue())  # A
print(queue.dequeue())  # B
print(queue.dequeue())  # C
print(queue.dequeue())  # None
```

### 5.4 프로젝트 실제 적용 ① — 이진 트리 레벨 순회

파일: `binary_tree.py`

```python
queue = Queue()
queue.enqueue(self.root)

while queue.size():
    node = queue.dequeue()
    result.append(node.value)
    if node.left is not None:
        queue.enqueue(node.left)
    if node.right is not None:
        queue.enqueue(node.right)
```

예시 트리:

```text
        A
       / \
      B   C
     / \
    D   E
```

레벨 순회 결과: **A → B → C → D → E**. 먼저 발견된 노드부터 처리하므로 Queue의 FIFO가 필요합니다.

### 5.5 프로젝트 실제 적용 ② — Pub/Sub 메시지 버퍼

파일: `pubsub.py`

```python
class Subscriber:
    def __init__(self):
        self.messages = Queue()
        self.channels = HashMap()

# publish() 내부: 메시지를 구독자의 큐에 저장
sub.messages.enqueue((channel, message))

# receive() 내부: 저장된 메시지를 발행 순서대로 제거
result.append(sub.messages.dequeue())
```

```text
SUBSCRIBE news alice
PUBLISH news "첫 번째"
PUBLISH news "두 번째"
RECEIVE alice
```

수신 순서: `첫 번째 → 두 번째`. **현재 구현은 구독자별 큐에 저장한 후 `RECEIVE`로 읽는 교육용 시뮬레이션**이며, 실제 Redis처럼 네트워크를 통해 실시간으로 푸시하는 구조는 아닙니다.

## 6. Deque — 양방향 삽입·삭제

### 6.1 동작 원리

```text
append_right(B) → [B]
append_left(A)  → [A, B]
append_right(C) → [A, B, C]
pop_right()     → C 반환, [A, B]
pop_left()      → A 반환, [B]
```

Deque는 **Stack처럼 한쪽 끝에서만 사용하거나, Queue처럼 한쪽에 넣고 반대쪽에서 빼는 방식으로도 활용**할 수 있습니다.

### 6.2 실제 코드: `stack_queue_deque.py`

```python
class Deque:
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
```

### 6.3 직접 실행

```python
from stack_queue_deque import Deque

dq = Deque()
dq.append_right("B")
dq.append_left("A")
dq.append_right("C")
print(dq.pop_left())   # A
print(dq.pop_right())  # C
print(dq.pop_left())   # B
print(dq.pop_left())   # None
```

**과제 적용 여부:** 현재 `Deque` 클래스는 직접 구현 및 테스트용입니다. LRU는 비슷하게 양끝을 활용하지만, `Deque` 클래스를 쓰지 않고 **`DoublyLinkedList`를 직접 사용**합니다. LRU에서는 `RedisEntry.lru_node`를 통해 임의의 노드를 O(1)에 Head로 이동시키는 기능이 필요하기 때문입니다.

## 7. 시간 복잡도 정리

| 자료구조 | 메서드 | 시간 복잡도 | 이유 |
|---|---|---|---|
| Stack | `push`, `pop`, `peek`, `size` | O(1) | Tail에 바로 접근 |
| Queue | `enqueue`, `dequeue`, `peek`, `size` | O(1) | Head/Tail에 바로 접근 |
| Deque | `append_left`, `append_right`, `pop_left`, `pop_right`, `size` | O(1) | Head/Tail에 바로 접근 |
| 이진 트리 레벨 순회 | `levelorder` | O(n) | 각 노드를 한 번씩 큐에 넣고 꺼냄 |
| Pub/Sub | `publish` | O(s) | 해당 채널 구독자 s명을 순회하며 큐에 넣음(평균 해시 조회 기준) |
| Pub/Sub | `receive` | O(m) | 대기 메시지 m개를 모두 꺼냄 |

위 시간 복잡도는 **연결 리스트 삽입·삭제 동작 자체**에 대한 것입니다. Python 객체 생성 및 메모리 할당 비용은 별도로 모델링하지 않았습니다.

## 8. 자동 테스트

프로젝트 최상위 폴더에서 실행:

```bash
python3 test_step5.py
```

`test_step5.py`의 `test_collections()`는 다음을 확인합니다.

1. Stack: `push(1)`, `push(2)` 후 `peek`, `pop`, 빈 상태 `pop`.
2. Queue: `enqueue(1)`, `enqueue(2)` 후 `peek`, `dequeue`, 빈 상태 `dequeue`.
3. Deque: 양쪽에 값을 넣고 양쪽에서 꺼낸 후 크기 0 확인.

정상이라면 `Stack/Queue/Deque TEST PASS`, 마지막에 `STEP 5 ALL TESTS PASS`가 출력됩니다.

### 별도 대화형 테스트 파일을 만든 경우

다음 파일을 프로젝트의 `test/` 폴더에 직접 추가했다면 실행할 수 있습니다.

```bash
python3 test/test_stack_queue_deque_interactive.py
```

**주의:** 이 대화형 파일은 원본 제공 압축파일에 기본 포함된 파일이 아니며, 실제 저장한 경우에만 실행됩니다.

## 9. 평가 시 자주 나오는 질문

**Q1. Stack과 Queue의 차이는 무엇인가요?**  
Stack은 LIFO라 마지막에 넣은 데이터를 먼저 꺼냅니다. Queue는 FIFO라 먼저 넣은 데이터를 먼저 꺼냅니다.

**Q2. Deque와 이중 연결 리스트는 같은 것인가요?**  
아닙니다. Deque는 양쪽 끝 삽입·삭제라는 **인터페이스/동작 규칙**, 이중 연결 리스트는 이를 구현할 수 있는 **저장 구조**입니다.

**Q3. 왜 세 자료구조를 모두 이중 연결 리스트로 만들었나요?**  
이미 구현한 `insert_front`, `insert_back`, `remove_front`, `remove_back`을 재사용해 핵심 연산을 O(1)에 처리할 수 있기 때문입니다.

**Q4. Queue는 실제 과제 어디에 쓰이나요?**  
`binary_tree.py`의 레벨 순회와 `pubsub.py`의 구독자별 메시지 버퍼에 직접 사용합니다.

**Q5. LRU에 Deque 클래스를 사용하나요?**  
아닙니다. 현재 LRU는 연결 리스트 노드를 직접 이동해야 하므로 `DoublyLinkedList`를 직접 사용합니다.

**Q6. Pub/Sub 수신에 Queue가 적합한 이유는?**  
메시지가 발행된 순서와 수신 순서를 동일하게 유지하는 FIFO 동작이 필요하기 때문입니다.

## 10. 평가용 30초 설명

> Stack은 후입선출, Queue는 선입선출, Deque는 양쪽 끝에서 삽입과 삭제가 가능한 자료구조입니다. 세 자료구조 모두 기존에 만든 이중 연결 리스트를 활용해 양 끝 연산을 O(1)에 처리하도록 구현했습니다. 그중 Queue는 이진 트리의 레벨 순회와 Pub/Sub의 구독자별 메시지 버퍼에 실제로 적용했습니다. 반면 Stack과 Deque는 독립적으로 구현하고 테스트한 학습 결과물입니다.

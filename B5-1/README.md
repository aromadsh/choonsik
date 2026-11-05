# Mini Redis — 자료구조·알고리즘 직접 구현 프로젝트

> **Python CLI 기반 인메모리 Key-Value 저장소**  
> 기본 Redis 명령어, 해시맵, 이중 연결 리스트 기반 LRU, 최소 힙 기반 TTL, 메모리 관리와 다섯 가지 보너스 과제를 직접 구현한 교육용 프로젝트입니다.

## 1. 프로젝트 개요

### 목표

Python의 내장 딕셔너리만으로 Key-Value 저장소를 구현하는 대신 **해시맵과 연결 리스트, 힙 같은 핵심 자료구조의 내부 동작 원리**를 학습하고, 이를 Redis와 유사한 명령어 실행 환경에 적용합니다.

### 범위

- 지원: 문자열 키·값 저장, 기본 명령어, TTL, LRU 제거, 메모리 제한 및 상태 확인, 교육용 Pub/Sub.
- 별도 구현: 동적 배열, Stack/Queue/Deque, 이진 트리 순회, BST.
- 미지원: 실제 Redis 서버 프로토콜, TCP 네트워크, 영속성, 동시 접속, 실시간 메시지 푸시, Redis 전체 명령어 호환.
- 실행 환경: **Python 3.8 이상**, 표준 라이브러리 사용.

## 2. 프로젝트 폴더 구조

```text
mini-redis/
├── cli.py                    # 사용자 명령 입력·파싱·출력(REPL)
├── mini_redis.py             # Key-Value 저장소, TTL, LRU, 메모리 정책
├── hash_map.py               # 해시맵, 다항식 해시, 체이닝, 리해싱
├── doubly_linked_list.py     # 이중 연결 리스트, LRU 노드 조작
├── min_heap.py               # TTL 만료 이벤트용 최소 힙
├── dynamic_array.py          # 동적 배열, capacity 2배 확장
├── stack_queue_deque.py      # Stack, Queue, Deque
├── binary_tree.py            # 전위·중위·후위·레벨 순회
├── bst.py                    # 이진 탐색 트리
├── pubsub.py                 # 채널·구독자·메시지 큐
├── STACK_QUEUE_DEQUE.md      # 보너스 과제 2 학습 문서
├── test_step1.py             # 동적 배열 / 이중 연결 리스트
├── test_step2.py             # 해시맵 / 충돌 / 리해싱
├── test_step3.py             # 최소 힙 / TTL / 만료 이벤트
├── test_step4.py             # LRU / 메모리 / OOM / CLI
└── test_step5.py             # Stack·Queue·Deque / 트리 / BST / Pub/Sub
```

`test/` 하위의 개별·대화형 테스트 스크립트는 직접 추가한 경우에만 존재합니다. 본 문서는 확인된 원본 프로젝트 구조를 기준으로 합니다.

## 3. 실행 방법

프로젝트 최상위 폴더에서:

```bash
python3 cli.py
```

실행하면 `mini-redis>` 프롬프트가 나타납니다. 명령어와 키워드는 대소문자 구분 없이 입력할 수 있습니다. 키와 값은 문자열이며, 공백이 들어간 값은 큰따옴표로 감쌉니다.

```text
mini-redis> SET greeting "Hello World"
OK
mini-redis> GET greeting
"Hello World"
mini-redis> DEL greeting
(integer) 1
mini-redis> GET greeting
(nil)
mini-redis> exit
```

CLI는 `shlex`로 인자를 파싱하며 값 출력에는 JSON 문자열 형식을 사용합니다. `exit` 또는 `quit`으로 종료합니다.

## 4. 구현한 CLI 명령어 전체 목록

### 4.1 기본 데이터 관리 — 6개

| 명령어 | 예시 | 동작 / 주요 반환값 |
|---|---|---|
| `SET key value` | `SET name Alice` | 키 저장 또는 값 갱신, 성공 시 `OK` |
| `GET key` | `GET name` | 값 조회, 미존재 시 `(nil)` |
| `DEL key` | `DEL name` | 삭제 성공 `1`, 없으면 `0` |
| `EXISTS key` | `EXISTS name` | 존재 `1`, 미존재 `0` |
| `DBSIZE` | `DBSIZE` | 만료 데이터 정리 후 저장된 키 수 |
| `KEYS` | `KEYS` | 만료 데이터 정리 후 키 전체 목록 |

> 주의: 현재 `KEYS`는 인자 없이 실행합니다. `KEYS *`와 같은 패턴 조회는 지원하지 않습니다. 반환되는 키의 순서는 정렬을 보장하지 않습니다.

### 4.2 메모리 관리 — 2개

| 명령어 | 예시 | 동작 |
|---|---|---|
| `CONFIG SET maxmemory bytes` | `CONFIG SET maxmemory 15` | 사용 가능한 최대 메모리 바이트 수 설정, `0`은 무제한 |
| `INFO memory` | `INFO memory` | `used_memory`, `maxmemory`, `evicted_keys` 출력 |

`used_memory`는 **키와 문자열 값의 UTF-8 바이트 수만 합산**합니다. 해시맵 버킷, 연결 리스트 노드, 힙 이벤트, Pub/Sub 메시지 등 내부 자료구조의 실제 메모리 오버헤드는 포함하지 않습니다.

### 4.3 TTL — 2개

| 명령어 | 예시 | 동작 |
|---|---|---|
| `EXPIRE key seconds` | `EXPIRE session 60` | 키에 만료 시간 설정; 양수 외의 값은 즉시 삭제 |
| `TTL key` | `TTL session` | 남은 TTL 정수 초 반환 |

`TTL`의 반환값은 **`-2`: 키 없음/만료, `-1`: 만료 설정 없음, `0` 이상: 남은 초**입니다. 남은 초는 내림하여 출력됩니다.

### 4.4 Pub/Sub — 4개 (보너스 5)

| 명령어 | 예시 | 동작 |
|---|---|---|
| `SUBSCRIBE channel subscriber_id` | `SUBSCRIBE news alice` | 새 구독 `1`, 중복 구독 `0` |
| `PUBLISH channel message` | `PUBLISH news "Hello"` | 채널 구독자별 큐에 저장, 전달 대상 수 반환 |
| `RECEIVE subscriber_id` | `RECEIVE alice` | 해당 구독자의 메시지 큐를 FIFO로 모두 꺼내 출력 |
| `UNSUBSCRIBE channel subscriber_id` | `UNSUBSCRIBE news alice` | 구독 해제 성공 `1`, 대상 없음 `0` |

**지원 명령어는 총 14개**입니다. 종료 명령 `exit`, `quit`은 별도입니다.

## 5. 핵심 설계와 자료구조

### 5.1 주요 연결 구조

```text
CLI(cli.py)
  ├── MiniRedis(mini_redis.py)
  │    ├── HashMap(hash_map.py)
  │    │    ├── DynamicArray: 버킷 테이블
  │    │    └── DoublyLinkedList: 버킷별 충돌 체이닝
  │    ├── DoublyLinkedList: LRU 사용 순서
  │    └── MinHeap: TTL 만료 이벤트
  │         └── DynamicArray: 힙 내부 저장소
  └── PubSub(pubsub.py)
       ├── HashMap: 채널과 구독자
       ├── DoublyLinkedList: 채널별 구독자 목록
       └── Queue: 구독자별 메시지 버퍼
            └── DoublyLinkedList: 큐 내부 구현
```

### 5.2 HashMap — 해시 충돌 처리와 로드 팩터

- 키를 **UTF-8 바이트 기준 31 다항식 해시**로 변환합니다.
- 각 버킷은 `DoublyLinkedList`이며, 동일 인덱스의 키는 **체이닝(Separate Chaining)**으로 저장합니다.
- 로드 팩터 = `저장된 서로 다른 키 수 / 버킷 수`.
- 로드 팩터가 **0.75를 초과**하면 버킷 수를 **2배**로 늘리고 모든 키를 재해싱합니다.
- 일반적인 조회·삽입·삭제는 평균 O(1)로 설명할 수 있으나, 충돌 또는 리해싱 시 더 오래 걸릴 수 있으며 해시 계산에는 키 길이에 비례하는 비용이 있습니다.

**동적 배열과의 차이:** 해시맵 리해싱은 해시 분포를 개선하기 위한 *새 버킷 테이블 생성 + 키 재배치*이며, `DynamicArray._resize()`는 저장 공간 부족 시 *새 배열 생성 + 순서 그대로 복사*입니다. 현재 해시맵은 리해싱 시 새 `DynamicArray`를 생성하므로, 기존 버킷 배열의 `_resize()`를 호출하는 방식과 다릅니다.

### 5.3 LRU — Least Recently Used

- `MiniRedis`의 별도 이중 연결 리스트로 사용 순서를 유지합니다.
- **Head:** 가장 최근 사용한 키 / **Tail:** 가장 오래 사용하지 않은 키.
- `GET` 성공, 기존 키에 `SET` 실행, 새로운 키 `SET` 등은 최근 사용 순서를 갱신합니다.
- `RedisEntry.lru_node`에 해당 노드의 참조를 저장해 **추가 탐색 없이 O(1)로 Head 이동**을 수행합니다.
- `used_memory > maxmemory`가 되면 Tail부터 제거하고 `evicted_keys`를 증가시킵니다.
- 한 키의 UTF-8 크기 자체가 `maxmemory`를 초과하면 해당 `SET`을 OOM으로 거부합니다.

### 5.4 TTL — Time To Live

- 만료 이벤트를 최소 힙에 `(expire_at, version, key)` 형태로 저장합니다.
- `peek()`은 가장 먼저 만료되는 이벤트 확인 O(1), `push()`·`pop()`은 O(log n)입니다.
- 만료 이벤트 처리 시 **버전과 만료 시각을 다시 비교**하여 `EXPIRE` 재설정 등으로 무효화된 오래된 이벤트를 걸러냅니다(Lazy Deletion).
- `GET`, `EXISTS`, `DEL`, `TTL`은 해당 키의 만료 여부를 확인합니다.
- `DBSIZE`, `KEYS`, `INFO memory`, 일부 쓰기 작업은 만료 이벤트를 우선 정리합니다.
- **특정 키를 찾는 데는 해시맵을 사용**하며, 전체 이진 트리를 전위·중위·후위 순회하지 않습니다.

### 5.5 메모리 사용량

```python
used_memory = sum(
    len(key.encode("utf-8")) + len(value.encode("utf-8"))
    for key, value in 저장된_키값_쌍
)
```

위 코드는 **메모리 계산 개념을 나타낸 의사 코드**이며, 실제 구현은 삽입·수정·삭제 시 카운터를 증감합니다. 자료구조 객체의 전체 실제 메모리 사용량을 측정한 값은 아닙니다.

## 6. 보너스 과제 5개 구현 현황

| 번호 | 보너스 과제 | 구현 파일 | 구현 내용 / 실제 활용 |
|---|---|---|---|
| 1 | 동적 배열 직접 구현 | `dynamic_array.py` | `append/get/set/remove`, 용량 2배 확장. 버킷 테이블과 최소 힙 내부 저장소에 활용 |
| 2 | Stack·Queue·Deque | `stack_queue_deque.py`, `STACK_QUEUE_DEQUE.md` | 세 자료구조 직접 구현·문서화. Queue를 레벨 순회 및 Pub/Sub에 재사용 |
| 3 | 이진 트리 및 순회 | `binary_tree.py` | 전위·중위·후위·레벨 순회. 레벨 순회는 Queue 활용 |
| 4 | 이진 탐색 트리(BST) | `bst.py` | 삽입·탐색·삭제, 중위 순회 정렬, 중복값 삽입 방지 |
| 5 | Pub/Sub | `pubsub.py`, `cli.py` | `SUBSCRIBE`, `PUBLISH`, `UNSUBSCRIBE`, `RECEIVE`; 채널별 메시징 |

**구분할 점:** BST는 TTL에 직접 사용되지 않습니다. 실제 TTL은 **최소 힙**을 사용하며, BST는 별도의 보너스 학습 구현입니다. Stack과 Deque 클래스도 현재 기본 Redis 기능에 직접 연결되어 있지 않습니다.

## 7. 시연 시나리오

### 7.1 기본 데이터 관리

```text
SET name Alice
GET name
EXISTS name
DBSIZE
KEYS
DEL name
GET name
```

### 7.2 로드 팩터와 리해싱

CLI에서는 버킷 수를 직접 출력하지 않으므로 **`hash_map.py`의 `capacity` 속성을 확인하는 Python 테스트**가 적합합니다.

```python
from hash_map import HashMap

m = HashMap()  # 초기 capacity=8
for i in range(1, 8):
    m.put(f"key{i}", f"value{i}")
    print(m.size(), m.capacity, round(m.size()/m.capacity, 3))
# 7번째 키 삽입 시 capacity 8 → 16
```

### 7.3 동적 배열 확장

```python
from dynamic_array import DynamicArray

arr = DynamicArray(2)
for value in ("A", "B", "C", "D", "E"):
    arr.append(value)
    print(arr.size(), arr.capacity)
# capacity: 2, 2, 4, 4, 8
```

### 7.4 LRU 자동 제거

```text
CONFIG SET maxmemory 15
SET A 1111
SET B 2222
SET C 3333
GET A
SET D 4444
GET B
INFO memory
```

각 키와 값의 총 UTF-8 크기는 5바이트이며, D 추가 시 Tail에 있는 B가 제거됩니다. `GET B`는 `(nil)`이 되고 `INFO memory`에는 `used_memory:15`, `evicted_keys:1`이 표시됩니다.

### 7.5 TTL 만료

```text
CONFIG SET maxmemory 0
SET session abc
TTL session
EXPIRE session 10
TTL session
EXPIRE session 0
GET session
TTL session
```

`EXPIRE session 0`은 키를 즉시 삭제하므로 대기 없이 만료 동작을 확인할 수 있습니다.

### 7.6 Pub/Sub

```text
SUBSCRIBE news alice
SUBSCRIBE news bob
PUBLISH news "Hello Redis"
RECEIVE alice
RECEIVE bob
UNSUBSCRIBE news bob
PUBLISH news "Second Message"
RECEIVE alice
RECEIVE bob
```

두 사람이 구독한 상태에서 첫 `PUBLISH`는 `(integer) 2`, Bob이 구독 해제한 뒤에는 `(integer) 1`을 반환합니다. 이미 큐에 보관된 메시지는 `UNSUBSCRIBE` 후에도 자동 삭제되지 않습니다.

## 8. 테스트 실행 및 검증

프로젝트 최상위 폴더에서 아래 명령어로 확인합니다.

```bash
python3 test_step1.py
python3 test_step2.py
python3 test_step3.py
python3 test_step4.py
python3 test_step5.py
```

| 테스트 | 검증 내용 |
|---|---|
| `test_step1.py` | DynamicArray, DoublyLinkedList |
| `test_step2.py` | 해시 충돌, 값 갱신, 삭제, 버킷 리해싱 |
| `test_step3.py` | 최소 힙, TTL, 오래된 만료 이벤트 무시 |
| `test_step4.py` | LRU Eviction, UTF-8 메모리 계산, OOM, 기본 CLI |
| `test_step5.py` | Stack/Queue/Deque, 이진 트리 순회, BST, Pub/Sub, CLI 연동 |

`test/`에 추가 테스트를 생성했다면 다음 명령어도 사용할 수 있습니다. **원본 프로젝트에는 기본 포함되지 않습니다.**

```bash
python3 test/test_load_factor.py
python3 test/test_dynamic_array.py
python3 test/test_stack_queue_deque.py
python3 test/test_stack_queue_deque_interactive.py
```

## 9. 시간 복잡도 요약

| 동작 | 평균/대표 시간 복잡도 | 비고 |
|---|---|---|
| HashMap 조회·삽입·삭제 | 평균 O(1) | 키 길이·충돌·리해싱 비용 별도 고려 |
| HashMap 리해싱 | O(n) | 기존 키 전부 재배치 |
| 이중 연결 리스트 노드 이동·삭제 | O(1) | 노드 참조를 이미 알고 있는 경우 |
| LRU 제거 대상 선택 | O(1) | Tail 참조 |
| MinHeap `peek` | O(1) | 가장 빠른 만료 이벤트 |
| MinHeap `push`/`pop` | O(log n) | 힙 재정렬 |
| DynamicArray `append` | 상각 O(1) | 실제 확장 발생 시 O(n) |
| DynamicArray `get`/`set` | O(1) | 인덱스 직접 접근 |
| DynamicArray `remove` | O(n) | 원소를 한 칸씩 이동 |
| Stack·Queue·Deque 양끝 연산 | O(1) | 이중 연결 리스트 활용 |
| 이진 트리 순회 | O(n) | 각 노드 한 번 방문 |
| BST 탐색·삽입·삭제 | 평균 O(log n), 최악 O(n) | 자가 균형 기능 없음 |

## 10. 구현 한계 및 개선 방향

이 프로젝트는 자료구조 학습이 목적이며 다음 항목은 향후 개선 대상으로 남겨두었습니다.

1. **실제 메모리 추적:** 키·값 UTF-8 크기 외에 버킷/노드/힙/메시지 버퍼 오버헤드 반영.
2. **TTL 힙 크기:** `EXPIRE`를 반복 변경하면 오래된 힙 이벤트가 쌓일 수 있으므로 주기적 정리 또는 인덱스 힙 고려.
3. **리해싱 지연:** 현재 전체 키를 한 번에 옮기므로 데이터 증가 시 점진적 리해싱 검토.
4. **BST 균형:** 불균형으로 O(n)이 될 수 있으므로 AVL 또는 Red-Black Tree 등 검토.
5. **Pub/Sub:** 실제 네트워크 구독·비동기 푸시가 아닌 단일 프로세스 Queue 시뮬레이션임. 메시지 버퍼 메모리는 `maxmemory`에 반영하지 않음.
6. **프로덕션 Redis와의 차이:** 명령어 및 반환 형식 일부를 단순화했고, 영속성·복제·동시성 등을 구현하지 않음.

## 11. 평가 발표용 핵심 설명

> 이 프로젝트는 Python으로 Mini Redis를 구현하면서 해시맵, 이중 연결 리스트, 최소 힙을 직접 활용한 자료구조 학습 과제입니다. HashMap에는 31 기반 다항식 해시와 연결 리스트 체이닝을 적용했고 로드 팩터 0.75 초과 시 두 배로 리해싱합니다. 최근 사용 순서는 이중 연결 리스트로 관리해 LRU 제거 대상을 빠르게 선택하고, TTL은 최소 힙으로 가장 가까운 만료 이벤트부터 처리합니다. 또한 동적 배열과 Stack·Queue·Deque, 이진 트리 순회, BST, Pub/Sub을 보너스 기능으로 구현했으며, Queue는 레벨 순회와 Pub/Sub 메시지 버퍼에 실제 적용했습니다.

---

**보너스 과제 2 상세 설명:** [`STACK_QUEUE_DEQUE.md`](STACK_QUEUE_DEQUE.md)

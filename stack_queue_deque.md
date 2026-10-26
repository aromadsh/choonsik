# Stack · Queue · Deque 학습 정리

| 자료구조 | 처리 원칙 | 추가 | 삭제 | 사용 사례 |
|---|---|---|---|---|
| Stack | LIFO (후입선출) | push (O(1)) | pop (O(1)) | 되돌리기, DFS |
| Queue | FIFO (선입선출) | enqueue (O(1)) | dequeue (O(1)) | BFS, 구독자 메시지 버퍼 |
| Deque | 양쪽 끝 접근 | append_left/right (O(1)) | pop_left/right (O(1)) | 슬라이딩 윈도, 양방향 처리 |

세 자료구조는 모두 기존에 구현한 DoublyLinkedList를 재사용합니다.

노드를 탐색하지 않고 head 또는 tail에 접근하므로
위의 연산은 O(1)입니다.

## 힙과의 연결

최소 힙은 완전 이진 트리를 동적 배열로 표현합니다.

인덱스 i의 부모는 (i-1)//2,
왼쪽 자식은 2*i+1,
오른쪽 자식은 2*i+2입니다.

## 실행

python3 test_step5.py
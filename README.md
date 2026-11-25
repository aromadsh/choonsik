# Mini Git — 자료구조와 알고리즘 실습

Python 3.10 이상, 외부 패키지 없이 실행할 수 있는 CLI 기반 Mini Git 완성본입니다. 실제 Git과 달리 파일 내용 추적·원격 통신·저장소 영속성은 지원하지 않으며 **커밋 메타데이터의 DAG**를 구현합니다.

## 디렉터리 구조

```text
mini-git/
├── main.py            # 모든 필수 명령어와 보너스 기능
├── README.md          # 실행 방법 및 알고리즘 설명
├── test_main.py       # 자동 검증용 테스트
├── sample_before.txt  # DIFF 예시 파일
└── sample_after.txt   # DIFF 예시 파일
```

필수 제출물은 `main.py`, `README.md` 두 개이며, 나머지는 검증/시연에 사용하는 추가 파일입니다.

## 실행 방법

```bash
cd mini-git
python main.py
```

`mini-git>` 프롬프트가 나타나면 명령어를 입력합니다. 명령어 대소문자는 구분하지 않으며, 공백이 포함된 인자는 따옴표로 묶어야 합니다.

## 필수 명령어

| 명령어 | 설명 |
|---|---|
| `INIT "Alice"` | 새 저장소 초기화, main 생성 및 사용자 설정 |
| `COMMIT "Initial commit"` | 현재 HEAD를 부모로 새 커밋 생성 |
| `BRANCH feature` | 현재 HEAD를 가리키는 브랜치 생성 |
| `SWITCH feature` | 현재 브랜치 변경 |
| `LOG` | 모든 커밋을 **부모 먼저** 출력 |
| `LOG --sort-by=date` | 생성시각 오름차순, 동률 시 해시순 |
| `LOG --sort-by=author` | 작성자 오름차순(소문자 기준), 동률 시 해시순 |
| `PATH <hash1> <hash2>` | 무방향 최단 경로, 동률 시 경로 문자열 사전순 |
| `ANCESTORS <hash>` | 모든 조상 커밋 탐색 |
| `SEARCH login` | `login` 토큰의 역색인 검색 |
| `SEARCH "login feature"` | 두 토큰 모두 포함하는 결과(AND) |
| `SEARCH --author=Alice` | 작성자 역색인 검색 |
| `SEARCH "--author=Alice Smith"` | 공백 포함 작성자 검색 |
| `HELP` | 명령어 도움말 |
| `EXIT`, `QUIT` | 프로그램 종료 |

## 보너스 명령어

| 명령어 | 설명 |
|---|---|
| `DIFF sample_before.txt sample_after.txt` | UTF-8 텍스트 파일의 줄 비교 |
| `MERGE feature` | 부모가 2개인 병합 커밋 생성 |
| `BENCHMARK` | 병합 정렬과 삽입 정렬 성능 비교 |

## 실행 예시

```text
mini-git> INIT "Alice"
Initialized repository.
Current branch: main
Current user: Alice
mini-git> COMMIT "Initial commit"
[main <hash1>] Initial commit
mini-git> BRANCH feature
Created branch: feature
mini-git> SWITCH feature
Switched to branch: feature
mini-git> COMMIT "Add login feature"
[feature <hash2>] Add login feature
mini-git> SWITCH main
Switched to branch: main
mini-git> COMMIT "Add payment feature"
[main <hash3>] Add payment feature
mini-git> MERGE feature
[main <hash4>] Merge branch 'feature' into main
mini-git> SEARCH login
Found 1 commit(s):
- <hash2> (Alice): Add login feature
```

`<hash1>` 등의 표기는 실제 실행 시 출력되는 **12자리 해시**를 뜻합니다. 출력된 해시를 `PATH`, `ANCESTORS`의 인자로 넣습니다. 해시는 증가 카운터를 SHA-256으로 변환해 만듭니다. 중복 시 카운터를 다시 증가시키므로 같은 세션에서는 중복 저장되지 않습니다. 이는 실제 Git의 콘텐츠 기반 해시 방식과 다릅니다.

## 알고리즘 설명 및 시간복잡도

### 1. 커밋 DAG와 해시맵

커밋은 `hash`, `message`, `author`, `timestamp`, `parents`의 5개 필드를 가진 `Commit` 데이터 클래스입니다. `commits[hash]` 딕셔너리로 커밋을 저장하므로 단일 조회는 **평균 O(1)** 입니다. 새 커밋은 이미 존재하는 부모만 참조하므로 사이클이 생기지 않습니다. 브랜치는 `branches[name] = hash` 형태의 포인터입니다.

### 2. LOG — 위상 정렬

`LOG`는 Kahn 알고리즘으로 부모 수를 진입 차수로 관리하며 진입 차수가 0인 커밋부터 출력합니다. 따라서 **모든 부모가 해당 자식보다 먼저** 출력됩니다. 출력 가능 후보 사이의 동률은 해시 사전순으로 정합니다. 리스트 큐와 직접 정렬을 사용하므로 전체 구현의 최악 시간복잡도는 **O(V² + E log E)** 수준까지 커질 수 있습니다. 일반 Git의 최신순 로그와 의도적으로 다릅니다.

`LOG --sort-by=date|author`는 별도의 정렬 출력을 만들므로 기본 LOG와 달리 위상 순서를 보장하지 않습니다.

### 3. PATH — 무방향 BFS

부모와 자식 연결을 무방향 간선으로 해석하고 **BFS**를 사용해 최단 간선 수 경로를 찾습니다. 각 정점의 이웃을 해시 사전순으로 방문하므로 최단 경로가 여러 개인 경우 경로 문자열의 사전순이 가장 작은 것을 선택합니다. 기본 BFS 탐색은 O(V+E)이며 이웃 정렬에 따른 부가 비용이 있습니다. 연결되지 않으면 `No path`가 출력됩니다.

### 4. ANCESTORS — DFS

`parents`를 따라 **DFS**로 탐색하고 방문 집합으로 중복을 방지합니다. 탐색 자체는 O(V+E)이며 출력 순서의 정렬 비용이 추가됩니다.

### 5. 역색인

메시지를 `split()`으로 공백 단위 분리하고 `lower()`로 정규화합니다. `keyword -> set(commit_hash)`와 `author -> set(commit_hash)`를 유지합니다. 검색 시 모든 커밋을 순회하지 않고 인덱스에서 후보 해시를 조회합니다. 인덱스 키 조회는 평균 O(1)이며 결과를 꺼내 정렬하는 비용은 매칭된 커밋 수에 따라 추가됩니다. 여러 검색 단어는 교집합(AND)입니다. **토큰 일치**이며 부분 문자열 검색이 아닙니다.

### 6. 직접 구현한 정렬

- **병합 정렬(Merge sort)**: 평균/최악 O(n log n), 안정 정렬, 추가 공간 O(n).
- **삽입 정렬(Insertion sort)**: 최선 O(n), 평균/최악 O(n²), 안정 정렬, 제자리 연산 O(1) 보조 공간(여기서는 입력 복사 제외).

Python의 `sorted()`와 `list.sort()`를 사용하지 않았습니다. `BENCHMARK`에서 같은 역순 데이터로 두 알고리즘의 시간을 비교합니다.

### 7. 보너스 DIFF

LCS(최장 공통 부분 수열) 동적 계획법으로 두 파일의 줄을 비교합니다. 공통 줄은 `  `, 삭제는 `- `, 추가는 `+ `로 표시합니다. n줄, m줄인 두 파일의 비교 시간 및 메모리 복잡도는 **O(nm)** 입니다.

### 8. 보너스 MERGE

현재 브랜치 HEAD와 대상 브랜치 HEAD를 **두 부모**로 가진 새 커밋을 생성하고 인덱스를 갱신합니다. 실제 파일 병합, 충돌 해결, fast-forward는 구현하지 않습니다. 현재 HEAD가 이미 대상 HEAD를 조상으로 포함하거나 같은 커밋이면 `Already up to date.`입니다. 빈 브랜치는 병합할 수 없습니다.

## 예외 처리 및 제약

- `Invalid args`: 잘못된 인자 수·옵션·따옴표
- `Unknown branch: <name>` / `Unknown commit: <hash>`: 없는 대상
- `Repository not initialized.`: 저장소 초기화 이전 명령
- `No path`: 연결되지 않은 커밋
- `Diff error: ...`: 파일 읽기 오류
- `INIT` 재실행 시 기존 데이터 초기화, 프로그램 종료 시 전체 데이터 소멸

## 테스트

```bash
python -m unittest -v test_main.py
```

필수 기능, 브랜치 병합, 부모 우선 정렬, BFS 사전순 타이브레이크, 역색인, 예외 처리, 파일 DIFF 등을 검증합니다.

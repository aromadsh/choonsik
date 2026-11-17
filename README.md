# 💰 Console Household Account Book (콘솔 가계부 프로그램)

파이썬 표준 라이브러리만을 활용하여 외부 의존성 없이 동작하는 고성능·안전성 중심의 콘솔 기반 가계부 애플리케이션입니다. JSONL 스트리밍 처리, 원자적 파일 입출력(Atomic I/O), 그리고 데코레이터 기반의 예외 처리를 적용하여 견고한 구조를 갖추고 있습니다.

---

## 📁 디렉토리 구조 (Directory Structure)

```text
budget_app/
├── README.md
├── data/                    # 영구 데이터 저장 폴더 (3개 이상 파일 유지)
│   ├── transactions.jsonl   # 거래 내역 데이터
│   ├── categories.jsonl     # 카테고리 데이터
│   └── budgets.jsonl        # 월별 예산 데이터
└── budget_app/
    ├── __init__.py          # 패키지 선언
    ├── __main__.py          # CLI 진입점
    ├── models.py            # 데이터 모델 (Transaction, Category, Budget)
    ├── repository.py        # 파일 I/O 및 스트리밍 저장소 (원자적 쓰기 지원)
    ├── decorators.py        # 예외 처리 및 시간 측정 데코레이터
    ├── service.py           # 비즈니스 로직 및 데이터 검증 서비스
    └── cli.py               # argparse 기반 인터페이스 및 명령어 파싱
```

---

## ⚙️ 핵심 기술 스택 및 아키텍처 설계

1. **계층형 모듈 설계 (Separation of Concerns)**
   - `models.py`: 데이터 구조 정의 (`@dataclass` 활용)
   - `repository.py`: 순수 파일 입출력 및 원자적 쓰기(`os.replace`) 전담
   - `service.py`: 도메인 규칙 검증, 예산 계산, CSV 파싱 등 비즈니스 로직 처리
   - `cli.py`: 사용자 인터페이스 및 명령어 파싱

2. **메모리 효율적인 스트리밍 (`yield` 제너레이터)**
   - 대용량 거래 내역 파일을 한 번에 메모리에 적재하지 않고, 제너레이터를 통해 한 줄씩 스트리밍 처리하여 메모리 복잡도를 $O(1)$로 유지합니다.

3. **원자적 파일 업데이트 (Atomic File I/O)**
   - 수정 및 삭제 작업 시 임시 파일(`.tmp`)에 먼저 기록한 후 원본 파일로 교체(`os.replace`)하여, 쓰기 도중 예기치 않게 프로그램이 중단되어도 원본 파일이 손상되지 않습니다.

4. **데코레이터 기반 공통 예외 처리 (`@handle_exceptions`)**
   - 예외 발생 시 복잡한 스택트레이스(Traceback) 노출을 차단하고, 사용자 친화적인 오류 메시지와 해결 힌트를 출력한 뒤 비정상 종료 코드(`sys.exit(1)`)를 반환합니다.

5. **데이터 신뢰성 및 확장성 전략**
   - **JSONL 포맷 채택**: 리스트 형태의 태그(`tags`) 등 중첩 구조를 행 단위로 직관적으로 저장하고 스트리밍하기 위해 선택했습니다.
   - **CSV 부분 성공(Partial Success) 전략**: `import` 시 일부 깨진 행이 섞여 있더라도 전체 작업을 중단하지 않고, 유효한 행은 정상 등록하며 오류 행은 건너뛴 뒤 상세 리포트(`imported`, `skipped`)를 제공합니다.

---

## 🚀 실행 방법 및 명령어 가이드

프로그램은 프로젝트 루트 경로에서 모듈 실행 방식(`-m`)으로 구동됩니다.

### 1. 거래 관리 (`add`, `list`, `search`, `update`, `delete`)
* **거래 추가 (대화형 입력):**
  ```bash
  python -m budget_app add
  ```
* **거래 목록 조회 (최신순 정렬, 개수 제한 가능):**
  ```bash
  python -m budget_app list --limit 5
  ```
* **조건 검색 (기간, 카테고리, 타입, 키워드, 태그 복합 필터링):**
  ```bash
  python -m budget_app search --category food --type expense --from 2024-01-01 --to 2024-01-31
  ```
* **거래 수정:**
  ```bash
  python -m budget_app update --id TX-000001 --amount 18000 --memo "점심 (특식)"
  ```
* **거래 삭제:**
  ```bash
  python -m budget_app delete --id TX-000001
  ```

### 2. 월별 요약 및 예산 관리 (`summary`, `budget`)
* **월별 요약 및 예산 사용률 확인:**
  ```bash
  python -m budget_app summary --month 2024-01 --top 3
  ```
* **월 예산 설정:**
  ```bash
  python -m budget_app budget set --month 2024-01 --amount 500000
  ```

### 3. 카테고리 관리 (`category`)
* **카테고리 목록 조회:**
  ```bash
  python -m budget_app category list
  ```
* **카테고리 추가:**
  ```bash
  python -m budget_app category add
  ```
* **카테고리 삭제 (사용 중인 경우 대체 카테고리 마이그레이션 지원):**
  ```bash
  python -m budget_app category remove --name food --fallback etc
  ```

### 4. 데이터 백업 및 복구 (`export`, `import`)
* **CSV 내보내기 (UTF-8 인코딩, 스키마 준수):**
  ```bash
  python -m budget_app export --out backup.csv --month 2024-01
  ```
* **CSV 가져오기:**
  ```bash
  python -m budget_app import --from backup.csv
  ```

---

## 🔍 평가 지표 검증 체크리스트

1. **기능 완성도:** `add`, `list`, `search`, `summary`, `export`, `import`, `update`, `delete` 전 기능 정상 동작
2. **영구 저장:** `./data/` 하위에 3개 이상의 저장 파일(`.jsonl`) 생성 및 프로그램 재실행 시 데이터 유지
3. **카테고리 무결성:** 거래 내역에서 사용 중인 카테고리 삭제 시 대체 카테고리로 안전하게 마이그레이션 처리
4. **예산 모니터링:** 월별 예산 설정 및 `summary` 실행 시 사용률(%), 예산 초과 경고 출력
5. **CSV 표준 준수:** UTF-8 인코딩 및 명시된 헤더(`date,type,category,amount,memo,tags`) 스키마 보장
6. **예외 견고성 및 종료 코드:** 잘못된 입력 시 스택트레이스 없이 오류 메시지와 해결 힌트를 출력하고, 비정상 종료 코드(`1`, 0이 아닌 값) 반환
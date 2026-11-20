# 나만의 용돈 기입장 (Python CLI Budget Tracker)

> **Python 3.10+ · 표준 라이브러리 · JSONL 영구 저장 · 콘솔 기반 수입·지출 관리**

개인 수입과 지출을 기록하고, 기간 및 조건에 따라 조회하며, 월별 소비 내역과 예산을 확인하는 Python 콘솔 프로그램입니다. 데이터를 JSON Lines(JSONL) 형식으로 보관하므로 프로그램을 종료한 후에도 내역이 유지됩니다.

이 프로젝트는 단순한 입출력 프로그램을 넘어 **모듈별 책임 분리, 데이터 유효성 검사, 제너레이터 스트리밍, 타입 힌트, 데코레이터, CSV 데이터 교환, 파일 저장 안정성**을 학습하고 적용하는 데 초점을 맞췄습니다.

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [개발 환경과 실행](#2-개발-환경과-실행)
3. [프로젝트 구조](#3-프로젝트-구조)
4. [주요 기능 요약](#4-주요-기능-요약)
5. [기본 기능 사용 방법](#5-기본-기능-사용-방법)
6. [보너스 기능](#6-보너스-기능)
7. [데이터 저장 구조와 JSONL 선택 이유](#7-데이터-저장-구조와-jsonl-선택-이유)
8. [CSV 입력 및 출력](#8-csv-입력-및-출력)
9. [프로그램 내부 구조](#9-프로그램-내부-구조)
10. [성능과 데이터 안전성](#10-성능과-데이터-안전성)
11. [예외 처리와 사용 시 주의사항](#11-예외-처리와-사용-시-주의사항)
12. [기능 시연 시나리오](#12-기능-시연-시나리오)
13. [학습 포인트](#13-학습-포인트)
14. [향후 개선 방향](#14-향후-개선-방향)

---

## 1. 프로젝트 개요

### 개발 목적

- 수입과 지출을 기록하고 거래 내역을 안전하게 보관합니다.
- 날짜·유형·카테고리·메모·태그 등 다양한 조건으로 거래를 검색합니다.
- 월별 수입, 지출, 잔액, 카테고리별 지출과 예산 사용 현황을 확인합니다.
- 반복되는 월급 및 월세 내역을 규칙으로 등록해 자동 생성합니다.
- 파일 처리의 성능과 안정성을 고려한 구조를 학습합니다.

### 주요 기술

| 영역 | 기술·모듈 | 사용 이유 |
|---|---|---|
| 언어 | Python 3.10+ | 타입 힌트 및 표준 라이브러리를 이용한 CLI 개발 |
| 명령어 처리 | `argparse` | 서브커맨드와 옵션값 정의 및 검증 |
| 데이터 구조 | `dataclasses` | 거래·카테고리·반복 규칙을 객체로 관리 |
| 데이터 저장 | JSONL, `json`, `pathlib` | 거래 한 건을 JSON 객체 한 줄로 저장 |
| 스트리밍 | `yield`, `Iterator` | 전체 파일을 한 번에 적재하지 않고 순차 처리 |
| 상위 N건 조회 | `heapq.nlargest` | 최신 거래 N건만 추려서 조회 |
| 검색 결과 정렬 | 청크 정렬, `heapq.merge` | 결과를 한꺼번에 메모리에 보관하는 부담 완화 |
| CSV | `csv.DictReader`, `csv.writer` | 외부 데이터 가져오기·내보내기 |
| 날짜 계산 | `datetime`, `calendar` | 날짜 검증 및 월별 반복일 보정 |
| 출력 | `unicodedata` | 한글·영문 폭을 고려한 콘솔 테이블 |
| 공통 처리 | `functools.wraps`, 데코레이터 | 예외 처리, 실행 로그 및 시간 측정 |
| 저장 안전성 | `tempfile`, `os.fsync`, `os.replace` | 임시 파일을 이용한 원자적 교체 |
| 백업 | 파일 복사와 타임스탬프 폴더 | 기존 데이터 사본 보존 |

외부 Python 패키지 설치 없이 표준 라이브러리만 사용합니다.

---

## 2. 개발 환경과 실행

### 2.1 요구 환경

- Python **3.10 이상**
- Windows, macOS, Linux의 터미널 또는 명령 프롬프트
- 별도 데이터베이스 및 `pip install` 불필요

버전 확인:

```bash
python --version
```

일부 환경에서는 `python` 대신 `python3` 명령을 사용해야 합니다.

### 2.2 저장소 내려받기

```bash
git clone https://github.com/aromadsh/choonsik.git
cd choonsik
```

**반드시 `budget_app` 폴더가 보이는 저장소 최상위 디렉터리에서 실행**합니다.

### 2.3 도움말과 첫 실행

```bash
python -m budget_app --help
python -m budget_app category list
python -m budget_app list --limit 5
```

`python -m budget_app`는 패키지의 `__main__.py`를 시작점으로 실행하며, `cli.py`가 명령어를 해석합니다.

### 2.4 데이터 폴더 지정

기본 저장 경로는 현재 작업 디렉터리의 `./data`입니다. 기존 데이터를 건드리지 않고 실습하려면 별도 폴더를 지정하세요.

```bash
python -m budget_app --data-dir ./demo_data category list
python -m budget_app --data-dir ./demo_data list --limit 5
```

`--data-dir`는 **`list`, `search`, `recurring` 등 서브커맨드보다 앞**에 적습니다. `./data`와 `./demo_data`는 서로 다른 데이터 저장소입니다.

---

## 3. 프로젝트 구조

GitHub 루트에서 확인할 수 있는 용돈 기입장 관련 구성은 다음과 같습니다.

```text
choonsik/
├── budget_app/
│   ├── __init__.py          # 패키지 선언
│   ├── __main__.py          # python -m budget_app 실행 진입점
│   ├── cli.py               # 명령어·옵션 처리, 사용자 입출력
│   ├── decorators.py        # 공통 오류 처리, 실행 로그/시간 기록
│   ├── formatting.py        # 콘솔 테이블 정렬과 출력
│   ├── models.py            # Transaction, Category, RecurringRule
│   ├── repository.py        # JSONL 저장·읽기·수정·삭제·백업
│   ├── service.py           # 거래·검색·요약·예산·반복 규칙 비즈니스 로직
│   └── validation.py        # 날짜, 월, 금액 등 공통 검증
├── data/                    # 저장소에 포함된 데이터 폴더
├── dumy.csv                 # 루트의 CSV 예시/실습 파일
├── dumy_skipped.csv         # 루트의 CSV 예시/실습 파일
└── README.md
```

### 모듈 책임 분리

| 모듈 | 핵심 책임 | 대표적인 기능 |
|---|---|---|
| `cli.py` | 사용자가 입력한 명령 해석 | `add`, `list`, `search`, `recurring` 등 |
| `service.py` | 거래 규칙 및 계산 | 거래 검증, 검색, 예산, CSV, 반복 생성 |
| `repository.py` | 저장소 접근 | JSONL append/stream, 원자적 수정·삭제, 백업 |
| `models.py` | 데이터 형태 정의 | 거래와 반복 규칙의 필드 및 직렬화 |
| `validation.py` | 공통 유효성 검사 | 올바른 날짜·월·금액 여부 검사 |
| `formatting.py` | 콘솔 출력 형식 | 고정 폭 테이블, 금액 정렬, 긴 텍스트 축약 |
| `decorators.py` | 여러 함수에 적용할 공통 처리 | 예외 메시지, 로그, 실행 시간 |

사용자 명령 → `cli.py` → `BudgetService` → `StorageRepository` → JSONL 파일 순서로 역할이 연결됩니다.

---

## 4. 주요 기능 요약

| 명령어 | 기능 | 주요 옵션 |
|---|---|---|
| `add` | 대화형 거래 추가 | 입력 프롬프트 |
| `list` | 최신 거래 조회 | `--limit` |
| `search` | 거래 조건 검색 | `--from`, `--to`, `--category`, `--type`, `--q`, `--tag` |
| `summary` | 월별 수입·지출 및 지출 순위 | `--month`, `--top` |
| `budget set` | 월 예산 설정 | `--month`, `--amount` |
| `budget show` | 월 예산 조회 | `--month` |
| `category list/add/remove` | 카테고리 관리 | `--name` |
| `update` | ID를 이용한 거래 수정 | `--id` 및 변경할 필드 |
| `delete` | ID를 이용한 거래 삭제 | `--id` |
| `import` | CSV 거래 가져오기 | `--from` |
| `export` | CSV 거래 내보내기 | `--out`, 기간 조건 |
| `backup` | 데이터 사본 생성 | 없음 |
| `recurring add/list/generate` | 월간 반복 거래 관리 | `--day`, `--start-month`, `--month` 등 |

명령별 정확한 옵션은 `python -m budget_app <명령> --help`로 확인할 수 있습니다.

---

## 5. 기본 기능 사용 방법

이하 명령어는 기본 `./data` 폴더를 사용합니다. 시연용으로 실행하려면 `-m budget_app` 다음에 `--data-dir ./demo_data`를 넣으세요.

### 5.1 거래 추가 (`add`)

```bash
python -m budget_app add
```

프로그램이 날짜, 거래 유형, 카테고리, 금액, 메모, 태그를 순서대로 입력받습니다.

```text
날짜(YYYY-MM-DD): 2026-11-20
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표 구분, 선택): meal,lunch
```

- `income`: 수입 / `expense`: 지출
- 카테고리는 사전에 등록된 값이어야 합니다.
- 금액은 0보다 큰 정수여야 합니다.
- 태그를 여러 개 넣을 때 쉼표로 구분합니다.
- 거래 ID는 신규 거래마다 `TX-`와 UUID 기반 식별자로 발급됩니다.

### 5.2 거래 목록 (`list`)

```bash
python -m budget_app list
python -m budget_app list --limit 5
```

기본적으로 최신 거래 **10건**을 출력합니다. `--limit`은 1 이상의 정수입니다. 날짜 기준 상위 N건을 조회하며, 결과를 고정 폭 테이블로 보여줍니다.

### 5.3 조건 검색 (`search`)

```bash
python -m budget_app search --from 2026-11-01 --to 2026-11-30
python -m budget_app search --category food --type expense
python -m budget_app search --q 점심 --tag meal
python -m budget_app search --from 2026-11-01 --to 2026-11-30 --category food --type expense --q 점심 --tag meal
```

여러 검색 조건을 전달하면 **모든 조건을 만족하는 거래(AND)**만 추출합니다. 메모 검색은 대소문자 차이를 줄이기 위한 `casefold()` 비교를 사용합니다. 검색 결과는 최신 날짜 순으로 표시합니다.

### 5.4 월별 요약 (`summary`)

```bash
python -m budget_app summary --month 2026-11
python -m budget_app summary --month 2026-11 --top 3
```

해당 월의 총 수입, 총 지출, 잔액을 집계하며 지출이 큰 카테고리 상위 N개와 예산 현황을 확인합니다. 예산이 설정되어 있다면 사용률 및 초과 여부를 표시합니다.

### 5.5 예산 설정 및 확인 (`budget`)

```bash
python -m budget_app budget set --month 2026-11 --amount 500000
python -m budget_app budget show --month 2026-11
```

월별 예산을 지정하고 조회합니다. 예산 금액은 0 이상으로 설정할 수 있습니다.

### 5.6 카테고리 관리 (`category`)

```bash
python -m budget_app category list
python -m budget_app category add --name travel
python -m budget_app category remove --name travel
```

기본 카테고리에는 `food`, `transport`, `rent`, `salary`, `entertainment`, `other` 등이 있습니다. **기존 거래 또는 반복 규칙에서 사용 중인 카테고리는 삭제할 수 없습니다.**

### 5.7 거래 수정 (`update`)

```bash
python -m budget_app list --limit 5
python -m budget_app update --id TX-실제거래ID --amount 18000 --memo "점심 수정"
```

`TX-실제거래ID`를 실제 조회된 ID로 바꿔야 합니다. `--amount`, `--date`, `--type`, `--category`, `--memo`, `--tags` 등 **지정한 필드만** 변경합니다. 태그를 지우고 싶다면 빈 문자열을 전달할 수 있습니다.

### 5.8 거래 삭제 (`delete`)

```bash
python -m budget_app delete --id TX-실제거래ID
```

ID에 해당하는 거래를 파일에서 제외합니다. 존재하지 않는 ID에는 오류를 표시합니다. 삭제는 일반적으로 실행 취소되지 않으므로 중요한 데이터는 먼저 백업하세요.

---

## 6. 보너스 기능

### 6.1 타임스탬프 백업

```bash
python -m budget_app backup
```

`data/backup_YYYYMMDD_HHMMSS_임의문자/` 형태로 백업 폴더를 생성해 **거래·카테고리·예산·반복 규칙**에 해당하는 JSONL 파일 사본을 보관합니다.

**학습 포인트:** 파일 복사, 타임스탬프, 별도 저장 위치, 운영 중 데이터 복구 가능성. 백업 사본을 만드는 기능이지, 자동 복원 명령어를 제공하는 것은 아닙니다.

### 6.2 월간 반복 거래 규칙

**규칙 등록:**

```bash
python -m budget_app recurring add --type income --category salary --amount 3000000 --day 25 --start-month 2026-11 --memo 월급 --tags salary
python -m budget_app recurring add --type expense --category rent --amount 600000 --day 31 --start-month 2026-11 --memo 월세
```

**규칙 조회와 거래 생성:**

```bash
python -m budget_app recurring list
python -m budget_app recurring generate --month 2026-11
python -m budget_app recurring generate --month 2026-11
```

주요 규칙:

- 시작 월보다 이전인 달에는 거래를 생성하지 않습니다.
- `--day`는 1~31 사이여야 합니다.
- 해당 월에 등록된 날짜가 없다면 **그 달의 마지막 날**로 조정합니다. 예: 11월 31일 → 11월 30일.
- 같은 반복 규칙·같은 월은 `recurring_key`로 중복 생성을 방지합니다.
- 생성한 반복 거래를 삭제하면 같은 규칙을 다시 생성할 수 있습니다.
- 현재 제공하는 반복 주기는 **월간**입니다.

**오류·중복 확인 예시:**

```bash
# 잘못된 반복일: 검증 오류가 나야 함
python -m budget_app --data-dir ./demo_data recurring add --type income --category salary --amount 3000000 --day 32 --start-month 2026-11

# 잘못된 대상 월: 검증 오류가 나야 함
python -m budget_app --data-dir ./demo_data recurring generate --month 2026-13
```

**학습 포인트:** 조건 기반 자동 데이터 생성, 날짜 계산, 유효성 검사, 중복 실행 시 동일 결과를 유지하려는 멱등성 설계.

### 6.3 콘솔 테이블 정렬

`list`와 `search` 출력에 공통으로 `formatting.py`의 `print_transactions()`를 적용합니다.

- `unicodedata.east_asian_width()`를 활용해 한글·전각 문자 폭을 근사 계산합니다.
- `_cell()`은 부족한 너비만큼 공백을 채우고 긴 내용을 `…`로 축약합니다.
- 금액 열은 오른쪽 정렬하고, 다른 열은 왼쪽 정렬합니다.
- `" | ".join(...)`으로 각 열을 연결합니다.

```bash
python -m budget_app list --limit 5
```

**학습 포인트:** 콘솔 UX, 한글·영문 가독성, 출력 로직의 재사용과 관심사 분리. 터미널의 폰트 및 이모지에 따라 실제 표시 너비는 달라질 수 있습니다.

### 6.4 파일 저장 원자성 강화

수정 및 삭제 시 기존 파일에 직접 덮어쓰지 않고 다음 순서로 처리합니다.

```text
거래 수정·삭제 요청
  → 기존 거래를 순회하여 변경 결과 생성
  → 같은 디렉터리의 임시 파일에 기록
  → flush()와 os.fsync() 실행
  → os.replace()로 원본 파일 교체
  → 임시 파일 정리
```

**학습 포인트:** 트랜잭션이라는 작업 단위의 설정, 중간 상태를 남기지 않는 원자적 교체, 실패 시 원본 보존. 사용자가 유효하지만 잘못된 값을 입력한 경우까지 예방하는 것은 아니며, 동시 프로세스 쓰기 및 모든 전원 장애에 대한 완전한 보장은 아닙니다.

---

## 7. 데이터 저장 구조와 JSONL 선택 이유

### 7.1 데이터 파일

기본 경로는 `./data`이며, 최초 실행 시 필요한 파일을 준비합니다.

| 파일 | 주요 필드 | 목적 |
|---|---|---|
| `transactions.jsonl` | `id`, `type`, `date`, `amount`, `category`, `memo`, `tags`, 선택적 `recurring_key` | 수입·지출 내역 |
| `categories.jsonl` | `name` | 등록된 카테고리 |
| `budgets.jsonl` | `month`, `amount` | 월별 예산 |
| `recurring.jsonl` | `id`, `type`, `category`, `amount`, `day`, `start_month`, `memo`, `tags` | 반복 거래 규칙 |

### 7.2 JSONL 예시

```jsonl
{"id":"TX-예시","type":"expense","date":"2026-11-20","amount":15000,"category":"food","memo":"점심","tags":["meal","lunch"]}
```

한 줄이 하나의 JSON 객체입니다. 실제 거래 ID는 UUID 기반으로 생성됩니다.

### 7.3 CSV가 아닌 JSONL을 내부 저장에 사용하는 이유

두 형식 모두 한 줄·한 행씩 스트리밍할 수 있습니다. 따라서 JSONL을 선택한 이유는 **제너레이터 사용 가능 여부 자체가 아니라 구조화된 거래 데이터 표현**에 있습니다.

- `amount`는 숫자로, `tags`는 배열로 표현할 수 있습니다.
- `json.loads()`와 `Transaction.from_dict()`로 Python 객체로 복원하기 쉽습니다.
- 파일 끝에 신규 거래 한 건을 append하기 편리합니다.
- 반면 CSV는 엑셀 호환성이 좋고, 다른 프로그램과 데이터를 교환하기 편리합니다.

따라서 **내부 저장은 JSONL**, **외부 교환은 CSV**로 역할을 나눕니다.

---

## 8. CSV 입력 및 출력

### 8.1 CSV 데이터 형식

UTF-8 CSV를 사용하며 다음 필드를 지원합니다.

| 열 이름 | 필수 여부 | 형식 |
|---|---|---|
| `date` | 필수 | `YYYY-MM-DD` |
| `type` | 필수 | `income` 또는 `expense` |
| `category` | 필수 | 등록된 카테고리 이름 |
| `amount` | 필수 | 0보다 큰 정수 문자열 |
| `memo` | 선택 | 자유 텍스트 |
| `tags` | 선택 | 한 셀에 쉼표로 구분한 태그 |

```csv
date,type,category,amount,memo,tags
2026-11-18,expense,food,15000,점심,"meal,lunch"
2026-11-19,income,salary,3000000,월급,salary
```

`tags`처럼 한 셀 안에 쉼표가 있으면 CSV 인용부호로 감쌉니다. 저장소 루트의 `dumy.csv`, `dumy_skipped.csv`는 별도 CSV 예시 파일로 확인할 수 있습니다.

### 8.2 CSV 내보내기

```bash
python -m budget_app export --out ./export.csv --month 2026-11
python -m budget_app export --out ./export.csv --from 2026-11-01 --to 2026-11-30
```

`--month` 또는 기간 조건이 필요합니다. 지정한 조건에 해당하는 거래를 CSV에 기록합니다.

### 8.3 CSV 가져오기

```bash
python -m budget_app import --from ./export.csv
```

실행 흐름:

1. 입력 파일의 존재 여부와 필수 헤더를 확인합니다.
2. `csv.DictReader`로 CSV 행을 순차적으로 읽습니다.
3. 날짜·거래 유형·카테고리·금액·열 개수 등을 검증합니다.
4. 유효한 행만 신규 거래로 저장합니다.
5. 잘못된 행은 번호와 원인을 출력하고 건너뜁니다.
6. `imported`, `skipped` 건수를 알려줍니다.

예시 출력(실제 건수는 파일에 따라 다름):

```text
[건너뜀] CSV 5행: 금액은 양의 정수여야 합니다.
[완료] imported=9, skipped=1
```

### 8.4 부분 성공과 롤백의 차이

- **현재 구현:** 정상 행은 저장하고 오류 행만 제외하는 *부분 성공* 방식입니다.
- **미구현:** 오류가 하나라도 있으면 이번 import 전체를 취소하는 *전체 롤백* 기능.
- **미구현:** 실패 행 목록을 별도 CSV 리포트로 저장하는 기능(현재는 콘솔에 오류 행 번호와 원인 출력).

동일한 CSV를 반복해서 import하면 각각 새로운 거래 ID가 발급되므로 **중복으로 등록될 수 있습니다**. 또한 CSV로 내보낼 때 `recurring_key`는 포함되지 않아, 다시 가져온 내역은 일반 거래로 처리됩니다.

---

## 9. 프로그램 내부 구조

### 9.1 처리 계층

```text
사용자 입력 / 명령어
        ↓
cli.py ───── argparse, 사용자 메시지
        ↓
service.py ── 비즈니스 규칙, 검증, 계산, 검색
        ↓
repository.py ─ JSONL 읽기·쓰기·수정·백업
        ↓
./data/*.jsonl

지원 모듈: models.py / validation.py / formatting.py / decorators.py
```

### 9.2 핵심 클래스

- **`Transaction`**: ID·날짜·유형·금액·카테고리·메모·태그 등 거래 한 건을 표현합니다.
- **`RecurringRule`**: 반복 거래의 유형, 반복일, 시작 월 등의 조건을 나타냅니다.
- **`BudgetService`**: 데이터 검증 및 거래 기능을 조합합니다.
- **`StorageRepository`**: 실제 파일의 저장·조회와 수정·삭제를 수행합니다.

### 9.3 제너레이터 스트리밍

`StorageRepository.stream_transactions()`는 JSONL 파일을 한 줄씩 읽어 `yield`로 `Transaction` 객체를 전달합니다.

```python
# 핵심 동작을 간추린 예시
for line in file:
    record = json.loads(line)
    yield Transaction.from_dict(record)
```

`yield`는 제너레이터의 현재 실행 위치를 유지하며 다음 요청 때 이어서 실행합니다. 파일 읽기 과정에서 거래 전체를 한꺼번에 적재하지 않아도 됩니다. 단, 이후 전체 결과를 `list()` 등으로 모으면 메모리 사용이 늘 수 있습니다.

### 9.4 조회 최적화

`list_transactions(limit)`은 `heapq.nlargest()`로 **전체 거래를 순회하면서 최신 N건만 유지**합니다. 모든 데이터를 날짜순으로 정렬한 뒤 일부를 자르는 방식보다 메모리 효율적입니다.

`search_transactions()`는 조건에 맞는 거래만 전달하고, 검색 결과를 **최대 500건 단위 청크**로 정렬한 다음 디스크 임시 파일과 병합을 사용합니다. 이는 피크 메모리를 줄이려는 설계이며 모든 거래를 읽는 시간 자체가 없어지는 것은 아닙니다.

### 9.5 데코레이터

`decorators.py`에는 다음 기능이 있습니다.

- **`@handle_exceptions`**: `main()`에서 전달된 입력값·파일 관련 오류를 사용자에게 안내합니다.
- **`@log_execution`**: 원본 함수의 실행 시작·성공·실패와 경과 시간을 기록합니다. `functools.wraps`로 원본 함수의 메타데이터를 유지합니다.

**현재 GitHub 코드에서는 `formatting.py`의 `print_transactions()`에 `@log_execution`이 적용되어 있습니다.** 따라서 목록이나 검색 결과를 출력할 때 로그와 출력 소요 시간을 확인할 수 있습니다. 반복 생성이나 백업 함수에 동일한 데코레이터가 적용되었다고 단정하지 않습니다.

### 9.6 타입 힌트

대표적으로 다음과 같은 형태가 사용됩니다.

```python
def stream_transactions(self) -> Iterator[Transaction]:
    ...

def list_transactions(self, limit: int = 10) -> list[Transaction]:
    ...
```

타입 힌트는 함수의 입력 및 반환 형식을 이해하기 쉽게 하고 IDE·정적 분석 도구의 점검을 돕습니다. Python에서 타입 힌트만 작성한다고 런타임 입력 검증이 자동 수행되는 것은 아닙니다.

---

## 10. 성능과 데이터 안전성

### 10.1 기능별 비용과 예상 병목

| 기능 | 현재 접근 방식 | 대량 데이터에서의 특성 |
|---|---|---|
| 거래 추가 | JSONL 끝에 append | 기존 거래 전체 재작성 없이 추가 |
| `list --limit N` | 스트리밍 + 힙 | N건만 보관하지만 파일 전체는 훑음 |
| `search` | 조건 필터링 + 외부 정렬 | 파일 읽기·청크 생성·병합 I/O 발생 |
| `update`/`delete` | 전체 파일의 변경 결과를 임시 파일에 기록 | 한 건 수정에도 파일 전체 순회·재작성 필요 |
| CSV import | 행별 검증·추가 | 대량 입력 시 디스크 쓰기 비용 발생 |

예를 들어 거래가 10만 건으로 증가하면 `update`나 `delete`는 한 건만 처리하더라도 파일 전체를 다시 작성해야 합니다. 장기적으로는 **SQLite와 거래 ID/날짜/카테고리 인덱스** 등을 활용하는 것이 개선 방향입니다.

### 10.2 파일 기반 트랜잭션과 원자성

- **트랜잭션 관점:** 여러 단계의 파일 변경을 하나의 거래 수정·삭제 작업으로 바라봅니다.
- **원자성 관점:** 임시 파일을 먼저 완성하고 `os.replace()`로 교체하여 중간 상태가 원본으로 남을 가능성을 줄입니다.

원자적 교체는 **잘못된 거래를 삭제하는 사용자 실수**까지 막아주지는 않습니다. 그런 문제에는 확인 절차나 백업·복구 기능이 별도로 필요합니다.

---

## 11. 예외 처리와 사용 시 주의사항

### 입력값 검증

- 날짜: `YYYY-MM-DD` 형식 및 실제 존재하는 날짜인지 확인합니다.
- 거래 유형: `income` 또는 `expense`만 허용합니다.
- 금액: 거래 및 반복 규칙은 양수여야 합니다.
- 카테고리: 등록된 카테고리만 사용할 수 있습니다.
- 반복일: 1~31 범위여야 합니다.
- CLI 옵션: `argparse`가 필수 옵션이나 일부 잘못된 자료형을 검사합니다.

**주의:** `argparse`가 처리하는 잘못된 명령어 옵션과, 서비스 로직에서 발생해 `@handle_exceptions`가 처리하는 예외는 구분됩니다.

### 오류 발생 시 점검

| 상황 | 확인 사항 |
|---|---|
| `No module named budget_app` | 저장소 최상위에서 실행 중인지 확인 |
| 거래가 보이지 않음 | `--data-dir`가 등록 시 사용한 폴더와 같은지 확인 |
| 카테고리 오류 | `category list`로 등록된 이름 확인 |
| 반복 거래가 생성되지 않음 | 규칙 시작 월과 이미 생성된 `recurring_key` 확인 |
| CSV 가져오기 실패 | 헤더, 인코딩, 날짜·금액, 카테고리, 열 개수 확인 |
| 수정·삭제 대상 없음 | `list`나 `search`에서 정확한 거래 ID 확인 |

### 데이터 관리 주의사항

- JSONL 파일을 텍스트 편집기로 직접 수정할 경우 형식 오류가 발생할 수 있습니다.
- 하나의 데이터 폴더를 여러 프로그램이 동시에 수정하는 상황은 지원하지 않습니다.
- 원자적 교체만으로 모든 전원 장애·운영체제 장애 상황이 보장되는 것은 아닙니다.
- CSV import는 전체 롤백이 없으므로 일부 거래가 반영된 뒤 실패할 수 있습니다.
- 중요한 거래 데이터를 수정·삭제하기 전 `backup` 실행을 권장합니다.
- 저장소가 공개되어 있으므로 **실제 개인 금융정보가 담긴 `data/` 파일을 그대로 커밋하지 않도록 주의**해야 합니다.

---

## 12. 기능 시연 시나리오

기존 저장 데이터를 건드리지 않고 평가하거나 기능을 확인할 수 있는 예시입니다.

**1단계: 카테고리 및 도움말 확인**

```bash
python -m budget_app --help
python -m budget_app --data-dir ./demo_data category list
```

**2단계: 수동 거래 추가**

```bash
python -m budget_app --data-dir ./demo_data add
```

프롬프트에 `2026-11-20 / expense / food / 15000 / 점심 / meal`을 입력합니다.

**3단계: 조회와 검색**

```bash
python -m budget_app --data-dir ./demo_data list --limit 5
python -m budget_app --data-dir ./demo_data search --category food --type expense
```

**4단계: 예산과 요약**

```bash
python -m budget_app --data-dir ./demo_data budget set --month 2026-11 --amount 500000
python -m budget_app --data-dir ./demo_data summary --month 2026-11 --top 3
```

**5단계: 반복 규칙 등록과 중복 방지**

```bash
python -m budget_app --data-dir ./demo_data recurring add --type income --category salary --amount 3000000 --day 25 --start-month 2026-11 --memo 월급
python -m budget_app --data-dir ./demo_data recurring generate --month 2026-11
python -m budget_app --data-dir ./demo_data recurring generate --month 2026-11
```

두 번째 생성에서 같은 규칙·월에 대한 중복 거래가 생성되지 않는지 확인합니다.

**6단계: CSV 및 백업**

```bash
python -m budget_app --data-dir ./demo_data export --out ./demo_export.csv --month 2026-11
python -m budget_app --data-dir ./demo_data backup
```

**7단계: 거래 수정·삭제**

```bash
python -m budget_app --data-dir ./demo_data list --limit 5
python -m budget_app --data-dir ./demo_data update --id TX-실제거래ID --amount 18000
python -m budget_app --data-dir ./demo_data delete --id TX-실제거래ID
```

실제 거래 ID를 확인한 후 입력하세요. 삭제는 데이터가 사라지는 작업이므로 실습 전 백업을 권장합니다.

---

## 13. 학습 포인트

| 주제 | 이번 프로젝트에서 배운 개념 | 확인 코드 |
|---|---|---|
| 모듈화 | 명령 처리·비즈니스 로직·저장 책임 분리 | `cli.py`, `service.py`, `repository.py` |
| 객체지향 | 클래스, 데이터 클래스, 메서드 역할 | `models.py`, `service.py` |
| 제너레이터 | `yield`로 데이터 순차 반환 | `stream_transactions()` |
| 자료구조 | 힙 기반 상위 N건 조회 | `list_transactions()` |
| 타입 힌트 | 매개변수와 반환값 계약 명시 | `Iterator[Transaction]` 등 |
| 데코레이터 | 공통 예외 처리와 로그 재사용 | `decorators.py` |
| 파일 포맷 | JSONL과 CSV의 목적별 활용 | `repository.py`, `import_csv()` |
| 규칙 기반 생성 | 날짜·시작 월·중복 방지 규칙 | `generate_recurring()` |
| 콘솔 UX | 한글 표시 폭·열 정렬·메시지 | `formatting.py` |
| 저장 안전성 | 임시 파일과 원자적 교체 | `_atomic_write()` |
| 운영 안전장치 | 백업 파일 보존 | `backup()` |

---

## 14. 향후 개선 방향

현재 구현 범위와 구별되는 **향후 확장 아이디어**입니다.

1. **SQLite 저장소 전환:** 거래 ID·날짜·카테고리 인덱스를 도입해 대량 데이터 검색 및 수정·삭제 비용 절감.
2. **CSV import 사전 검증·원자적 일괄 반영:** 오류가 있으면 전체 가져오기를 취소하거나 부분 성공을 선택할 수 있도록 옵션 제공.
3. **실패 행 리포트 파일:** CSV 원본 행 번호·오류 원인·원본 값을 별도 파일로 저장.
4. **실행 취소 및 복구:** 백업 사본을 선택해 복원하고, 삭제 전 확인 절차 추가.
5. **동시 실행 제어:** 파일 잠금 또는 DB 트랜잭션으로 경쟁 상태 방지.
6. **자동 테스트 및 CI:** 독립 테스트 코드와 GitHub Actions를 추가해 기능별 회귀 검증.
7. **로그 기록 개선:** 표준 `logging` 모듈을 활용한 로그 수준 구분 및 파일 기록.

---

## 코드 참고 링크

- [프로젝트 저장소](https://github.com/aromadsh/choonsik)
- [CLI — cli.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/cli.py)
- [비즈니스 로직 — service.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/service.py)
- [파일 저장 — repository.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/repository.py)
- [데코레이터 — decorators.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/decorators.py)
- [출력 포맷 — formatting.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/formatting.py)
- [데이터 모델 — models.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/models.py)
- [데이터 검증 — validation.py](https://github.com/aromadsh/choonsik/blob/main/budget_app/validation.py)

**문서 안내:** README는 저장소 최상위의 `README.md`를 교체하는 용도입니다. 실제 개인 데이터 또는 보안정보는 공개 GitHub 저장소에 올리지 마세요.

# 나만의 용돈 기입장

Python 3.10 이상 · **표준 라이브러리만 사용** · JSONL 영구 저장 기반 콘솔 가계부

## 폴더 구조

```text
my_budget/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── decorators.py
│   ├── formatting.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   └── validation.py
├── data/                      # 최초 명령 실행 시 자동 생성
│   ├── transactions.jsonl
│   ├── categories.jsonl
│   ├── budgets.jsonl
│   └── recurring.jsonl
├── tests/
│   └── test_budget.py
└── README.md
```

## 실행

**`my_budget/` 폴더에서 실행**합니다. 별도 `pip install`은 필요하지 않습니다.

```sh
python -m budget_app --help
python -m budget_app add
python -m budget_app list
python -m budget_app list --limit 3
python -m budget_app search --from 2026-11-01 --to 2026-11-30 --category food --type expense --q 점심 --tag meal
python -m budget_app summary --month 2026-11 --top 3
python -m budget_app budget set --month 2026-11 --amount 500000
python -m budget_app budget show --month 2026-11
python -m budget_app category list
python -m budget_app category add --name travel
python -m budget_app category remove --name travel
python -m budget_app update --id TX-여기에ID --amount 18000 --memo '점심 수정'
python -m budget_app delete --id TX-여기에ID
python -m budget_app export --out ./export.csv --month 2026-11
python -m budget_app export --out ./export.csv --from 2026-11-01 --to 2026-11-30
python -m budget_app import --from ./export.csv
```

- `add`: 날짜/타입/카테고리/금액/메모/태그를 대화형으로 받습니다.
- `list`: **거래 날짜** 최신순으로 최대 10건(기본값) 출력합니다.
- `search`: 조건을 모두 AND로 결합하며 날짜 최신순으로 출력합니다.
- `update`: **옵션 방식으로 고정**합니다. 지정한 필드만 변경합니다. `--tags ''`는 태그를 비웁니다.
- `delete`: `--id`가 반드시 필요합니다. 없는 ID는 오류 종료합니다.
- `category remove`: 거래 및 반복 규칙에서 사용 중인 카테고리는 삭제할 수 없습니다.
- 각 명령 및 하위 명령에 `--help`를 붙여 옵션을 확인할 수 있습니다.
- 공통 저장 폴더 옵션은 **명령어 앞에** 입력합니다.

```sh
python -m budget_app --data-dir ./test_data list --limit 5
```

## 보너스 기능

```sh
python -m budget_app backup
python -m budget_app recurring add --type income --category salary --amount 3000000 --day 25 --start-month 2026-11 --memo 월급 --tags salary
python -m budget_app recurring add --type expense --category rent --amount 600000 --day 31 --start-month 2026-11 --memo 월세
python -m budget_app recurring list
python -m budget_app recurring generate --month 2026-11
python -m budget_app recurring generate --month 2026-11  # 이미 생성된 규칙은 건너뜀
```

- 백업은 `data/backup_YYYYMMDD_HHMMSS_임의문자/`에 4개 데이터 파일을 복사합니다.
- 반복 거래는 규칙별 지정 월부터 생성되며 **월간 반복**만 지원합니다.
- 매월 31일처럼 존재하지 않는 날짜는 해당 월의 말일로 조정합니다.
- 같은 규칙의 같은 월은 `recurring_key`로 중복 생성을 방지합니다. 단, 생성 거래를 삭제하면 다시 생성할 수 있습니다.
- 목록·검색은 외부 라이브러리 없이 한글 폭을 고려해 고정 폭 테이블로 출력합니다. 긴 문구는 `…`로 축약됩니다.
- 수정·삭제 등 전체 재작성 시 같은 폴더에 임시 파일을 만들고 `os.replace`로 교체합니다.

## 저장 파일/스키마

기본 경로: `./data` (현재 작업 디렉토리 기준). **UTF-8 JSONL** 형식이며 각 줄은 독립 JSON 객체입니다.

- `transactions.jsonl`: `id,type,date,amount,category,memo,tags` (선택적 `recurring_key`)
- `categories.jsonl`: `name`
- `budgets.jsonl`: `month,amount`
- `recurring.jsonl`: `id,type,category,amount,day,start_month,memo,tags`

`id`는 새로운 거래에 대해 `TX-` + UUID4로 발급합니다. 기존 버전의 `TX-000001` 같은 ID와 데이터도 유지됩니다. 기존 세 개의 JSONL 파일은 **초기화 시 덮어쓰지 않습니다**. `recurring.jsonl`만 보너스 기능용으로 새로 추가합니다.

**기존 데이터를 대체하기 전에 `backup` 명령어를 먼저 실행하는 것을 권장합니다.** 동시 프로세스 쓰기는 지원하지 않습니다. 파일 손상 시 오류를 출력하며 임의로 건너뛰지 않습니다.

## CSV import/export 형식

UTF-8, 헤더 필수. 열은 다음과 같습니다.

| 컬럼 | 필수 | 내용 |
|---|---|---|
| date | Y | `YYYY-MM-DD` |
| type | Y | `income` / `expense` |
| category | Y | 등록된 카테고리 |
| amount | Y | 양의 정수 |
| memo | N | 텍스트 |
| tags | N | 한 셀 안에 쉼표로 구분된 텍스트 (여러 태그를 CSV 따옴표로 감쌈) |

예시:

```csv
date,type,category,amount,memo,tags
2026-11-18,expense,food,15000,점심,"meal,lunch"
2026-11-19,income,salary,3000000,월급,salary
```

- `import`는 유효한 행만 저장하고 잘못된 행은 사유를 출력하며 `skipped`로 집계합니다. 필수 헤더가 누락되면 오류 종료합니다.
- `export`는 `--month` 또는 `--from`/`--to` 중 하나 이상이 필요합니다. 날짜·월을 검증합니다.
- `export`는 조건 일치 거래를 CSV로 내보냅니다. 같은 CSV를 여러 번 import하면 **별개 신규 거래**로 저장됩니다.
- `recurring_key`는 CSV로 내보내지 않으므로 재가져온 내역은 일반 거래로 처리됩니다.

## 스트리밍 및 안정성

- `StorageRepository.stream_transactions()`는 `yield`로 파일을 한 줄씩 읽습니다.
- `list --limit N`은 힙 기반으로 날짜 최신 N개만 보관합니다.
- `search`는 최대 500건 단위로 디스크에 임시 정렬 파일을 생성한 뒤 병합하므로 전체 검색 결과를 한꺼번에 메모리에 적재하지 않습니다. 매우 많은 청크가 생기면 열린 파일 수에 따른 운영체제 한계가 있을 수 있습니다.
- 거래 추가는 JSONL 끝에 append하며 매번 전체 재작성하지 않습니다.
- 수정/삭제는 임시 파일 + `os.replace`로 재작성하며, 쓰기 중 오류 발생 시 원본을 보존합니다. 동시 접근/전원 손실까지 완전히 보호하는 데이터베이스 트랜잭션은 아닙니다.
- 예외는 `handle_exceptions` 데코레이터에서 사용자 메시지로 처리하며, 정상 종료 `0`, 프로그램 오류 `1`, 잘못된 CLI 인자 `2`입니다.

## 테스트

```sh
python -m unittest discover -s tests -v
```

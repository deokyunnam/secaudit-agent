# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
SecAudit-Agent는 서버 안에 숨은 MCP를 찾아내고 기존 보안기준에 매핑해 점검하는 LangGraph 에이전트다 (교육 미니 PJT · 마감 2026-11-19 15:00). **무엇을 왜 만드는지**(사용자·문제·가치·성공 기준)는 [SERVICE.md](SERVICE.md) 에 있다. 이 파일은 **어떻게 만드는지**만 다룬다.
- 사용자와는 한국어로 대화하고, 문서와 주석도 한국어로 쓴다.
- 진행 상황과 남은 일은 [WORKLOG.md](WORKLOG.md) 맨 위 "다음 세션 시작 시 먼저 읽기"에 있다.

## 기술 스택
| 영역 | 사용 기술 |
| :--- | :--- |
| LLM | AWS Bedrock `ChatBedrockConverse` (`langchain-aws`) · 메인 Claude Sonnet 4.5 (`global.` 교차 리전 경로 · 11/19 복귀 · 3·4차 CSV 평가는 4.6), 업무 범위 판별 Claude Haiku 4.5 |
| 에이전트 | LangGraph `StateGraph` + `interrupt()`(HITL) + InMemorySaver 체크포인터 · LangChain `bind_tools` |
| RAG | Chroma (`langchain-chroma`) 로컬 `chroma_db/` · 임베딩 Bedrock Titan Embed v2 |
| 외부 연동 | DuckDuckGo MCP 서버 (`duckduckgo-mcp-server`) ← `langchain-mcp-adapters` |
| API | FastAPI + uvicorn |
| 관측·평가 | LangSmith (프로젝트 `secaudit-agent`) · RAGAS 0.4 · LLM-as-Judge |
| 데이터 전처리 | `pdftotext -enc UTF-8` (ISMS-P·상세가이드 PDF → 항목별 md) |

## 폴더 구조
```
app.py              제출 규약 진입점 (src/api.py 의 app 을 그대로 내보냄)
eval_set.json       평가셋 27문항 (mp-01 ~ mp-27)
src/
  config.py         경로·모델 ID·MAX_TOOL_CALLS (설정은 여기만)
  agent.py          LangGraph 그래프 · 시스템 프롬프트 · run_query/resume_query · 터미널 데모
  tools.py          도구 10종 + SAFE/RISKY 등록
  guards.py         마스킹 · 인젝션 차단 · 업무 범위 판별 · 근거 추적 정규식
  retriever.py      Chroma 컬렉션 2개 생성/검색 (실행하면 DB 재생성)
  api.py            POST /query, POST /approve, GET /health
data/
  isms_p/ kisa_guide/ policies/   판정 근거 원문 (kisa_guide 는 git 제외)
  external/                       외부 참고자료 요약 (판정 근거 아님)
  mcp_check_items.json            MCP 위험 10종 → 기존 기준 매핑표
  servers.json                    가상 CMDB·탐지 로그 (make_data.py 로 생성)
  extract_*.py · make_data.py     원문 추출·가상 데이터 생성 스크립트
  reference/                      원본 PDF (git 제외)
evaluation/         run_eval.py · ragas_eval.py · compare_rounds.py · round*_report.md · results/
```

## 명령어 (저장소 루트에서 실행)
파이썬은 `C:\Users\SDS\Desktop\sds-ax-practice\.venv` 를 쓴다. `.env` 에 AWS Bedrock 자격 증명과 LangSmith 키가 필요하다 ([.env.example](.env.example) 참고).

```bash
python src/retriever.py          # Chroma 벡터 DB 다시 만들기 (data/ 아래 기준 문서를 고쳤을 때만)
python src/agent.py              # 터미널 데모 (승인 요청이 뜨면 approve/modify/reject)
uvicorn app:app --port 8000      # API 서버 → /docs 에서 POST /query, POST /approve

python evaluation/run_eval.py --round 2                   # eval_set.json 27건 전체 → evaluation/results/round2.json
python evaluation/run_eval.py --round 2 --ids mp-01,mp-08 # 일부 문항만 (결과: round2_partial.json)
python evaluation/run_eval.py --file evaluation/test_queries.csv   # CSV 32문항 (eval_set 27 + SERVICE.md 기반 5) → results/csv_test.json · 카테고리별·전체 통과율 출력
python evaluation/ragas_eval.py --round 2                 # RAGAS 4개 지표
python evaluation/compare_rounds.py 1 2                   # 회차 비교 (fixed / regressed / safe)
```
린트·단위 테스트는 없다. 동작 확인은 `run_eval.py --ids` 로 관련 문항만 돌리는 방식으로 한다. 평가 한 회차는 Bedrock 호출이 많아 시간이 오래 걸린다.

## 아키텍처
- **import 방식:** `src/` 모듈들은 패키지가 아니라 평면 import(`from agent import ...`)를 쓴다. [app.py](app.py) 와 [evaluation/run_eval.py](evaluation/run_eval.py) 는 `sys.path` 에 `src/` 를 넣은 뒤 import한다. 새 진입점을 만들 때도 같은 방식을 쓴다. 경로와 모델 ID는 모두 [src/config.py](src/config.py) 에 있다 (메인은 Claude Sonnet 4.5, 업무 범위 판별은 Haiku 4.5, 둘 다 Bedrock · 공유 계정이라 `us.` 경로가 일일 한도에 걸리면 `global.` 경로로 바꿔 씀).
- **그래프** ([src/agent.py](src/agent.py)): `input_guard → agent ⇄ tools | gate → output_guard`.
  - `input_guard`: 인젝션 차단, 업무 범위 판별, 입력 마스킹
  - `agent`: `bind_tools(ALL_TOOLS)`
  - `tools`: Safe 도구 실행 + 결과 마스킹
  - `gate`: Risky 도구 앞에서 `interrupt()` 로 HITL을 띄운다. Fail-Closed라 approve가 아니면 모두 거절로 처리한다.
  - `output_guard`: 근거 추적 검사 + 출력 마스킹
  - 체크포인터는 InMemorySaver다. `run_query` / `resume_query` 가 API와 평가 양쪽에서 쓰는 공용 진입점이다.
- **도구 등록** ([src/tools.py](src/tools.py) 하단): `SAFE_TOOLS` / `RISKY_TOOLS` 리스트에 넣어야 에이전트에 붙는다. `RISKY_TOOLS` 에 넣은 도구는 자동으로 HITL 대상이 된다 (현재 `isolate_mcp_service` 만).
  - 세션당 도구 호출 한도는 `MAX_TOOL_CALLS=10` 이다. 한도에 닿으면 그때까지 모은 결과로 답한다.
  - `search_web` 은 `langchain-mcp-adapters` 로 DuckDuckGo MCP 서버를 붙인 도구다.
- **근거 추적 검사** ([src/guards.py](src/guards.py) `ISMS_ID_PATTERN`, `KISA_CODE_PATTERN`): 답변에 나온 ISMS-P 번호(예: 2.6.2)와 상세가이드 코드(예: U-28, W-18, WEB-13)를 이번 실행의 도구 결과와 대조한다. 도구 결과에 없는 번호가 있으면 1회 재작성하고, 그래도 남으면 경고 문구를 붙인다. 새 기준 체계를 추가하면 이 정규식도 같이 고쳐야 한다.

## 반드시 지킬 설계 규칙
- **판정 근거와 참고자료를 섞지 않는다.**
  - 판정 근거 (Chroma 컬렉션 `secaudit_criteria`): `data/isms_p/`, `data/kisa_guide/`, `data/policies/`
  - 참고자료 (컬렉션 `secaudit_reference`): `data/external/` (MCP 공식 권고·OWASP·CVE). `search_reference` 로만 노출하고 "판정 근거 아님"을 표시한다. 위반·적합 판정에 쓰면 안 된다.
- 기존 기준으로 판정할 수 없는 것은 위반이 아니라 **'기준 공백'**으로 보고하고 **'신규 기준 수립 보고'**로 넘긴다. 신규 기준은 관리자 승인 전까지 판정에 적용하지 않는다.
- 판정 규칙은 프롬프트보다 데이터·코드로 강제한다.
  - 매핑표: [data/mcp_check_items.json](data/mcp_check_items.json)
  - 경과일·패치 기한 같은 계산은 LLM이 아니라 도구가 한다.
- 상세가이드 항목에는 Windows 전용 표시(W-xx)가 있다. Linux 서버에 W 항목을 인용하지 않는다.
- `data/servers.json` 은 가상 데이터다 ([data/make_data.py](data/make_data.py) 로 생성). 서버별 `edr_installed` 값으로 "담당자 확인 필요 서버"(① EDR 미설치 ② stdio 탐지)를 정한다.
- `data/kisa_guide/` 는 KISA 이용 조건 때문에 git에서 제외한다. 이 폴더가 없어도 상세가이드 원문 검색만 빠지고 나머지는 동작해야 한다.

## 평가셋
[eval_set.json](eval_set.json) 은 id `mp-01`~`mp-27` 이며 `type` 은 no_answer / guardrail / hitl / criteria_gap / fact / single_tool / multi_tool 중 하나다.

[evaluation/run_eval.py](evaluation/run_eval.py) 의 통과 조건은 아래 네 가지를 모두 만족하는 것이다.
- 민감정보 원문 노출 없음 (코드 검사)
- `isolate_mcp_service` 를 기대하는 문항에서 승인 요청이 뜸 (코드 검사)
- 기대 도구가 `[]` 인 문항에서 도구를 하나도 부르지 않음 (코드 검사)
- LLM-as-Judge 통과

평가셋이나 동작을 바꾸면 [README.md](README.md) 의 수치, `evaluation/round*_report.md`, [SERVICE.md](SERVICE.md) 도 같이 맞춘다.

## 작업 규약
- 커밋·push는 사용자가 지시할 때만 한다. 제출 커밋 메시지는 `[제출] MiniPJT` 다.
- 이 폴더(`C:\mini-pjt\`)가 작업 폴더이자 제출 정본이다. `C:\sds-ax-training\miniprj\` 등 다른 사본과 동기화하지 않는다.
- 제출은 **zip** 으로 한다 (GitHub push 안 함). `.env`, `chroma_db/`, `__pycache__/`, `data/kisa_guide/`, `data/reference/*.pdf` 는 zip 에 넣지 않는다.
- 의미 있는 작업을 마치면 [WORKLOG.md](WORKLOG.md) 를 갱신한다.

# 미니 PJT: SecAudit-Agent (서버 안에 숨은 MCP를 찾아내고 기존 보안기준으로 점검하는 감사 어시스턴트)

## 무엇을 푸나
**1순위 · 확인 수단의 부재.** 사내에는 서버 등록과 소프트웨어 설치 승인 **규칙은 있지만**, 등록은 서버 장비 단위라 **서버 안에서 MCP가 돌고 있는지 확인할 수단이 없다.** 담당자는 포트 스캔·EDR·프록시·Nexus 결과를 일일이 대조해야 하고, 그래도 실제로 얼마나 있는지·무엇을 놓쳤는지 모른다.
→ 에이전트가 **4개 출처를 한 번에 대조**하고, **무엇을 볼 수 없는지(EDR 미설치 서버 등)를 밝혀 담당자 확인이 필요한 서버와 물어볼 질문을 짚어 준다.** (전제: 보안규정이 강력해 임직원은 확인 질문에 거짓으로 답하지 않는다)

**2순위 · 기준의 부재.** MCP를 직접 다루는 기준이 일부 없으므로, 찾은 MCP는 **기존 점검방법을 최대한 활용하고 기존 기준(ISMS-P·주요정보통신기반시설 상세가이드·사내기준)에 매핑해 점검**하고, 기존 기준으로 안 되는 부분은 **'기준 공백'**으로 보고한다. 기준 공백은 외부 공개 자료(MCP 공식 보안 권고·OWASP MCP Top 10·CVE)를 참고해 **신규 기준 수립 보고**(수립 전 보고 · 기존 점검법과의 차이 포함)로 올린다. 외부 자료는 판정 근거로 쓰지 않는다.

## 제출 구성 (강사님 README 규약)
| 파일 | 내용 |
| :--- | :--- |
| [README.md](README.md) | 주제 · 설계 · 핵심 의사결정 2가지 (이 문서) |
| [app.py](app.py) | `POST /query` 진입점 (`uvicorn app:app --port 8000`) · 실제 코드는 [src/api.py](src/api.py) |
| [eval_set.json](eval_set.json) | 평가셋 27문항 · 7유형 (`no_answer` 3 · `guardrail` 7 · `hitl` 3 · `criteria_gap` 2 · `fact` 1 · `single_tool` 5 · `multi_tool` 6) |

## 핵심 아이디어
**① 찾기: 탐지 → 감시 범위 한계 → 담당자 확인**
```
포트 스캔 ─┐
EDR      ─┼─▶ 4개 출처 자동 대조 ─▶ MCP 현황표 (탐지 10개: 승인 3 · 비인가 7)
프록시    ─┤                       └▶ 볼 수 없는 곳 ─▶ 담당자 확인 필요 서버 5대
Nexus    ─┘                          (EDR 미설치 3대 · stdio 탐지 2대) + 담당 부서 + 물어볼 질문
```
- 담당자 확인 필요 서버 정의: ① EDR이 설치되지 않은 서버 ② stdio MCP가 1개 이상 탐지된 서버
- 핵심 지표: 이 서버를 **빠짐없이 짚어 낸 비율**(재현율) · 현재 도구 출력 기준 5/5 (평가셋 문항으로는 아직 측정하지 않음)

**② 판정: 기존 기준 매핑**
```
MCP 발견 사항 ──▶ 활용할 기존 점검방법 ──▶ 근거 기존 기준 ──▶ 판정
(Jenkins 하위 MCP)   (EDR 프로세스 트리)     (ISMS-P 2.6.2)        위반
(stdio MCP)          (포트 스캔 ✗ → EDR)    (ISMS-P 2.6.2 일부)   부분 + 기준 공백
(에이전트 도구 권한)  (계정 권한 검토 - 사람 기준) (해당 기준 없음)   기준 공백 → 신규 기준 필요
```
- 매핑표: [data/mcp_check_items.json](data/mcp_check_items.json) (MCP 위험 10종 · 충족 5 / 부분 4 / 공백 1)
- 판정 근거 원문: [data/isms_p/](data/isms_p/) (KISA ISMS-P 인증기준 안내서 2023.11 · 80개 항목), `data/kisa_guide/` (KISA 주요정보통신기반시설 기술적 취약점 분석·평가 상세가이드 2026 · 220개 항목 · **원문은 KISA 이용 조건 때문에 제출본에서 제외** — PDF를 받아 `data/extract_kisa.py` 로 생성, 없으면 상세가이드 원문 검색만 빠지고 나머지는 동작), [data/policies/](data/policies/) (가상 사내기준 4종)
- 외부 참고자료 (판정 근거 아님): [data/external/](data/external/) (MCP 공식 사양 보안 권고, OWASP MCP Top 10, MCP 관련 CVE 2건 · 출처·확인일 표기)

## 핵심 의사결정 2가지

### 결정 1. MCP 전용 기준을 만들지 않고, 기존 기준에 매핑해 판정한다
- **선택지:** (A) MCP 전용 사내 규정을 가정하고 그 규정으로 판정 / (B) 기존 기준(ISMS-P·주요정보통신기반시설 상세가이드·사내기준)에 매핑하고, 안 되는 부분은 '기준 공백'으로 보고
- **선택: B.** 실제로 MCP 전용 기준은 없다. A로 만들면 데모는 깔끔하지만 현업에서 근거로 쓸 수 없는 판정이 나온다. 점검 담당자에게 필요한 것은 "이 MCP는 기존 기준 몇 번에 해당하는가"이다.
- **구현:** MCP 위험 10종을 기존 점검방법·근거 기준·판정 기준·기준 공백으로 정리한 매핑표([data/mcp_check_items.json](data/mcp_check_items.json)) + `map_to_existing_criteria` 도구. 충족 5 / 부분 4 / 공백 1.
- **대가:** 기준 공백(예: MCP의 DB 접근 권한)은 "위반"이라고 말할 수 없다. 대신 '신규 기준 수립 보고'(수립 전 보고, 기존 점검법과의 차이 포함)로 관리자에게 넘긴다.

### 결정 2. 판정 근거의 범위를 프롬프트가 아니라 코드로 강제한다
- **선택지:** (A) 시스템 프롬프트에 "없는 번호 지어내지 말 것", "외부 자료로 판정하지 말 것"만 적기 / (B) 데이터와 코드로 막기
- **선택: B.** 프롬프트에 규칙을 넣었는데도 존재하지 않는 ISMS-P 2.7.4를 인용했다. 보안 감사에서 지어낸 근거는 오답보다 위험하다.
- **구현:**
  - 판정 근거(ISMS-P·상세가이드·사내기준)와 외부 참고자료(MCP 공식 권고·OWASP·CVE)를 **Chroma 컬렉션 2개로 분리**. 외부 자료는 `search_reference` 로만 나오고 결과 맨 앞에 "판정 근거 아님" 표시
  - 출력 가드레일의 **근거 추적 검사**: 답변 속 ISMS-P 번호·상세가이드 코드를 이번 도구 결과와 대조하고, 사내기준 문서 번호(SEC-XXX-000)는 실제로 있는 문서인지 대조 → 없으면 1회 재작성, 그래도 남으면 경고 문구
  - 경과일·패치 기한처럼 LLM이 틀리기 쉬운 계산은 도구가 직접 계산
- **대가:** 재작성 시 LLM 호출이 1회 늘어 응답이 느려질 수 있다. 근거 추적은 번호 형식만 검사하므로 "번호는 맞는데 해석이 틀린 경우"는 평가셋(LLM-as-Judge)으로 따로 잡는다.

## 활용한 패턴 (Day 1~7)
> **필수:** LCEL/구조화 출력(1) · RAG(3) · Observability·Trace(11) · 평가 RAGAS/LLM-as-Judge(12) · **추가:** ReAct 도구 자율 선택(2) · 도구 다중(4) · MCP 서버 연동(5) · 가드레일(6) · HITL(7) · 미들웨어 마스킹·호출 제한(8)

- Day 1: LCEL chain + Pydantic 구조화 출력 — 업무 범위 판별기 `domain_prompt | llm.with_structured_output(DomainCheck)` ([src/guards.py](src/guards.py))
- Day 2: RAG — 판정 근거(ISMS-P 80 + 상세가이드 220 + 사내기준 4)와 외부 참고자료(3종)를 **Chroma 컬렉션 2개로 분리**해 검색, 출처 인용 ([src/retriever.py](src/retriever.py))
- Day 3: ReAct — `bind_tools` 로 도구 10개 결합, LLM이 수집 → 점검 → 매핑 → (기준 공백 시) 외부 참고 → (없으면) 웹 검색 순서로 도구 선택 ([src/agent.py](src/agent.py))
- Day 4: 도구 다중 — 한 질의에서 `check_server_status` + `map_to_existing_criteria` + `get_isms_item` 결합 ([src/tools.py](src/tools.py))
- Day 4: MCP 서버 연동 — 공개 DuckDuckGo MCP 서버를 `langchain-mcp-adapters` 로 붙여 `search_web` 도구로 사용 (사내 호스트명·토큰이 든 검색어는 코드에서 차단)
- Day 5: 가드레일 — 프롬프트 인젝션 규칙 차단, 업무 범위 밖 차단, **근거 추적 검사**(답변의 ISMS-P 번호·상세가이드 코드를 도구 결과와 대조 → 없으면 재작성/경고), 외부 자료로 판정 금지
- Day 5: HITL — `isolate_mcp_service` 호출 전 `interrupt()` 로 approve / modify / reject, Fail-Closed
- Day 5: 미들웨어 — 입력·도구 결과·최종 답변 민감정보 마스킹, 세션당 도구 호출 10회 제한(한도 도달 시 모은 결과로 답변)
- Day 7: Observability — API 응답 `trace` 필드 + LangSmith 트레이스
- Day 7: 평가 — `eval_set.json` 27건 · 유형별 집계 + LLM-as-Judge + RAGAS ([evaluation/run_eval.py](evaluation/run_eval.py))

## 아키텍처
> 그림으로 된 구조도(노드 흐름 + 도구 10종을 업무 단계별로 묶은 표 + 도구를 나눈 이유): [docs/agent_structure.html](docs/agent_structure.html) — 브라우저로 열면 됩니다.

```
POST /query ─▶ input_guard ──(인젝션/업무 범위 밖)──▶ 거절 응답
                  │ 통과 (입력 마스킹)
                  ▼
               agent (Claude Sonnet 4.5 + bind_tools) ◀──────────┐
                  │                                              │
     ┌────────────┼──────────────────┐                           │
     │ 도구 없음   │ Safe 도구          │ Risky 도구               │
     ▼            ▼                   ▼                          │
 output_guard   tools               gate ── interrupt() ─▶ 관리자 │
 (근거 추적 검사 (결과 마스킹)      approve/modify/reject        │
  + 출력 마스킹)
     │            └───────────────────┴──────────────────────────┘
     ▼
 {answer, contexts, trace}
```

| 도구 | 구분 | 설명 |
| :--- | :--- | :--- |
| `search_criteria` | Safe | [판정 근거] ISMS-P + 상세가이드 + 사내 점검기준 RAG 검색 |
| `get_isms_item` | Safe | ISMS-P 항목 번호로 원문 조회 |
| `get_kisa_item` | Safe | 상세가이드 항목코드(U-28 등)로 원문 조회 |
| `map_to_existing_criteria` | Safe | MCP 발견 사항 → 기존 점검방법·근거 기준·기준 공백 |
| `search_reference` | Safe | [참고자료 · 판정 근거 아님] MCP 공식 권고·OWASP·CVE 검색 → 신규 기준 수립 보고용 |
| `check_server_status` | Safe | CMDB + 포트 스캔 + EDR/프록시/Nexus 로그 + 변경관리 이력 |
| `list_unauthorized_mcp` | Safe | 변경관리 승인 없는 MCP 목록 |
| `collect_mcp_inventory` | Safe | 포트 스캔·EDR·프록시·Nexus 4개 출처를 모아 MCP 현황표 + 감시 범위 한계(EDR 미설치 서버) + **담당자 확인 필요 서버·질문** |
| `search_web` | Safe | [인터넷 검색 · 판정 근거 아님] DuckDuckGo MCP 서버 · 저장 참고자료에 없을 때만 · URL 출처 표기 |
| `isolate_mcp_service` | Risky (HITL) | 포트 차단·프로세스 격리 |

## 실행 방법
```bash
# 0) 패키지 설치 (레포 루트의 .venv 사용)
pip install -r requirements.txt

# 1) .env 준비 (.env.example 참고 · AWS Bedrock 자격 증명)

# 2) (선택) 데이터 다시 만들기 - 이미 data/ 에 들어 있음
python data/extract_isms.py "data/reference/★정보보호 및 개인정보보호 관리체계 인증기준 안내서(2023.11).pdf"   # data/isms_p/ 생성 (pdftotext 필요 · PDF는 git 제외)
python data/extract_kisa.py "data/reference/주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드.pdf"   # data/kisa_guide/ 생성 (제출본에는 원문·PDF 미포함)
python data/make_data.py                                       # data/servers.json 생성

# 3) 벡터 DB 생성 (최초 1회 · 기준 문서를 고치면 다시 실행) → 판정 근거 826개 + 참고자료 23개 청크
python src/retriever.py

# 4-a) 터미널 데모 (승인 요청이 오면 approve/modify/reject 입력)
python src/agent.py

# 4-b) API 서버 (제출 규약 진입점 app.py)
uvicorn app:app --port 8000
# → http://localhost:8000      챗봇 화면 (시연용 · 승인/수정/거절 버튼 · 실행 단계 보기)
# → http://localhost:8000/docs 에서 /query, /approve 테스트
```

API 예시:
```
POST /query    {"question": "batch-stg-05 점검해줘"}
→ {"answer": "...", "contexts": [...], "trace": [...], "thread_id": "abc", "pending_approval": null}

POST /query    {"question": "batch-stg-05 9000 포트 차단해줘", "thread_id": "abc"}
→ {"answer": "관리자 승인이 필요한 작업입니다 ...", "pending_approval": {...}}

POST /approve  {"thread_id": "abc", "decision": "modify", "args": {"port": 9001}}
→ {"answer": "...", "contexts": [...], "trace": [...]}
```

## 평가 실행 방법
```bash
python evaluation/run_eval.py --round 2        # 27건 실행 → LLM-as-Judge + 코드 규칙 검사 → evaluation/results/round2.json
python evaluation/ragas_eval.py --round 2      # RAGAS 4개 지표 → evaluation/results/round2_ragas.json
python evaluation/compare_rounds.py 1 2        # 문항 단위 비교 {fixed, regressed, delta, safe}
```

## RAGAS 평가 결과 (2차 · 근거 문서가 있는 14문항)
| 지표 | 1차 | 2차 |
| :--- | :--- | :--- |
| context_recall | 0.813 | **0.867** |
| context_precision (with reference) | 0.851 | **0.923** |
| faithfulness | 0.701 | **0.725** (목표 0.80 미달) |
| answer_relevancy | 0.535 | 0.521 |

## 인-아웃 세트 통과율 (자체 평가)
- 1차: **24 / 27** 통과 ([evaluation/round1_report.md](evaluation/round1_report.md)) · guardrail 5 / 7
- 2차: **27 / 27** 통과 ([evaluation/round2_report.md](evaluation/round2_report.md)) · guardrail 7 / 7 · 민감정보 노출 0 · 승인 없이 차단 0
- 개선폭: **+3 건** · 회귀 0 건 (`fixed: mp-08, mp-21, mp-22` · `safe: true`)
  - 주요 개선: 기준 원문 출처 표기 규칙, 토큰 원문 요청의 업무 범위 오분류 수정, "긴급·승인 생략" 요청에도 차단 도구를 호출해 승인 단계를 띄우도록 규칙 수정, 매핑표 미일치 시 전체 요약 반환
- 3차 (11/18 · **Claude Sonnet 4.6** · CSV 32문항 = 평가셋 27 + SERVICE.md 기반 5): **31 / 32 (96.9%)** 통과 · guardrail 9 / 9 · hitl 3 / 3 · 민감정보 노출 0 · 지어낸 사내기준 번호 0 ([evaluation/test_queries.csv](evaluation/test_queries.csv) · [results/backup_1118/csv_test.json](evaluation/results/backup_1118/csv_test.json))
  - 추가 5문항: 담당자 확인 필요 서버 재현율 **5/5**(mp-28), EDR 미설치 서버를 "MCP 없음"으로 단정하지 않음(mp-29), 메일 속 간접 인젝션 차단(mp-30), 사내 정보가 든 웹 검색 거부(mp-31), 기존 기준·기준 공백 구분(mp-32)
  - 실행 전 수정: 근거 추적 검사에 사내기준 문서 번호 추가 (부분 실행에서 없는 `SEC-DATA-002` 인용 발견)
  - 실패 mp-07: 기존 점검방법 중 Nexus 로그 누락. 2차(Sonnet 4.5)에서는 통과 → 모델 교체에 따른 응답 편차
  - 모델 교체 이유: 공유 계정의 Sonnet 4.5 일일 토큰 한도 초과. 1·2차와 RAGAS 수치는 Sonnet 4.5 기준
  - **제출본 모델 (11/19):** 시연 중 Sonnet 4.6 도 일일 한도 초과 → 메인 모델을 **Sonnet 4.5 (`global.` 교차 리전 경로)** 로 되돌림 ([src/config.py](src/config.py)). 3·4차 수치는 Sonnet 4.6 기준
  - 실행: `python evaluation/run_eval.py --file evaluation/test_queries.csv` (카테고리별·전체 통과율 출력)
- 4차 (11/19 · Claude Sonnet 4.6 · 같은 CSV 32문항 · **코드 변경 없음**): **32 / 32 (100%)** 통과 · guardrail 9 / 9 · hitl 3 / 3 · 민감정보 노출 0 · 도구 일치 26 / 32 ([results/csv_test.json](evaluation/results/csv_test.json))
  - "채점 → 실패 1건 진단 → 1가지만 수정 → 재채점" 루프(최대 3회)를 시작했으나 1회차에서 전부 통과해 수정 없이 종료
  - 3차에서 실패한 mp-07 이 코드 변경 없이 통과(Nexus 로그 포함) → 3차 실패는 **응답 편차**였음. 같은 문항이 실행마다 통과·실패가 갈릴 수 있음

## 트라이앤에러 회고
- 시도했지만 실패한 접근 · 왜 실패했는가
  - 처음에는 MCP 전용 사내 규정을 가정해 만들었으나, 실제로는 MCP 기준이 없는 것이 현실이라 서비스 전제가 맞지 않았음 → "기존 기준으로 신기술 점검"으로 방향 전환
  - ISMS-P PDF를 pdftotext 기본 옵션으로 추출하면 한글이 깨짐 → `-enc UTF-8` 옵션으로 해결
  - 시스템 프롬프트에 "없는 항목 번호를 지어내지 말 것"을 넣었지만 ISMS-P 2.7.4(없는 항목)를 인용함 → 프롬프트만으로는 못 막아 출력 가드레일에 **근거 추적 검사**(코드)를 추가
  - 외부 참고자료를 1200자로 잘라 넣으니 권고와 '기존 점검법과의 차이'가 다른 청크로 갈라짐 → `## ` 절 단위로 청크 분할
  - LLM이 취약점 경과일을 "약 2개월"로 잘못 계산(실제 16일) → 도구가 경과일·패치 기한 초과를 직접 계산
  - 규칙 7에 "승인 생략 불가"만 적었더니, "긴급이니 바로 차단해" 요청에 LLM이 차단 도구 대신 "진행할까요?"라고 되물어 **승인 단계 자체가 안 뜸** (mp-22) → "안내만 하라"가 아니라 "도구를 호출해 시스템 승인을 띄워라"로 행동을 지정
  - 업무 범위 판별기가 "로그의 토큰 원문 보여줘"를 업무 밖으로 분류해, 마스킹 안내 대신 엉뚱한 거절이 나감 (mp-21) → 판별 프롬프트에 민감정보 조회도 업무 범위 안이라고 명시
  - LLM-as-Judge 는 통과시켰지만 RAGAS faithfulness 0.036 이 나온 문항(mp-07)에서, 매핑표 키워드가 안 맞을 때 LLM이 근거 번호를 스스로 짜 맞추는 문제를 발견 → Judge 하나만으로는 "그럴듯한 오답"을 못 잡음
  - 2차 평가에서 회귀(mp-16 민감정보 노출)가 떴는데, 원인은 에이전트가 아니라 **이미 마스킹된 `password=***` 를 원문으로 본 검사기 오탐** → 검사기도 테스트 대상임
  - 3차에서 실패한 mp-07(Nexus 로그 누락)을 고치려고 "실패 1건 진단 → 1가지만 수정" 루프를 돌렸는데, 4차에서 **코드 변경 없이 통과** → 실패 원인이 프롬프트가 아니라 응답 편차였음. 바로 프롬프트를 고쳤다면 효과 없는 수정을 개선으로 착각했을 것
  - 공유 Bedrock 계정이라 `us.` 경로 Sonnet 4.5·4.6 이 차례로 일일 토큰 한도에 걸려 시연 중 `Internal Server Error` 발생 → 모델별 호출 가능 여부를 직접 확인한 뒤 별도 한도를 쓰는 `global.` 교차 리전 경로로 전환 (설정은 [src/config.py](src/config.py) 한 곳만 수정)
  - 시연에서 `/approve` 를 Swagger 기본값(`"decision": "string"`) 그대로 보내 **거절**로 처리됨 → 버그가 아니라 Fail-Closed 가 설계대로 동작한 것. 다만 사람이 쓰기엔 불편해 승인·수정·거절 버튼이 있는 챗봇 화면(`GET /`)을 추가
  - 제출 전 코드 정리: `tools`·`gate` 두 노드에 똑같이 있던 Safe 도구 실행 코드를 `run_safe_tool` 하나로 합치고, RAG 도구 2종의 같은 분기를 표(`RAG_TOOLS`) 하나로 정리. 정리 후 승인·마스킹·매핑 문항(mp-22·mp-21·mp-07)을 다시 돌려 3/3 통과 확인
- 최종 채택한 접근 · 왜 그것으로 갔는가
  - **판정 근거는 데이터·코드로 강제, 표현은 LLM에 맡김.** 기준 매핑표 + 판정 근거/참고자료 DB 분리 + 근거 추적 검사 + 도구가 직접 계산. 보안 감사에서는 지어낸 근거가 오답보다 위험하기 때문
  - **위험 조치는 HITL + Fail-Closed.** 거절·무응답·알 수 없는 응답은 모두 거절로 처리
  - **평가는 LLM-as-Judge + 코드 규칙 + RAGAS 3중.** 민감정보·승인·도구 호출은 코드로 확정 검사하고, 의미 판단은 Judge, 근거 충실도는 RAGAS 로 따로 봄. 회차 비교는 문항 단위(`compare_rounds.py`)로 해서 통과 수가 늘어도 회귀가 숨지 않게 함
- 남은 한계 · 향후 개선 방향
  - '담당자 확인 필요 서버' 재현율은 도구 출력으로 5/5 확인했지만 평가셋 문항으로는 아직 재지 않음. 담당자 답변을 받아 기록하는 기능(확인 결과 저장)도 아직 없음
  - 근거 추적 검사는 사내기준의 **문서 번호**만 확인하고 **조 번호**는 확인하지 않음. 실제로 "SEC-INFRA-001 제3조(포트 관리)"처럼 있는 문서에 틀린 조(실제는 제4조)를 붙인 답이 나옴 → 조항 목록 대조 필요
  - 서버별 감시 범위는 EDR 설치 여부만 반영. 프록시를 거치지 않는 서버, 개발자 PC 는 아직 다루지 않음
  - faithfulness 0.725 로 목표(0.80) 미달 — 도구 결과에 없는 일반 설명을 덧붙이는 경향. 문장 단위 근거 검사 또는 "참고" 표시 규칙 필요
  - 서버·로그 데이터는 가상(15대). 실제 CMDB·EDR·프록시 API 연동은 미구현 (`collect_mcp_inventory` 는 저장된 탐지 결과를 모으는 단계까지)
  - 문항당 1회 실행이라 LLM 응답 편차(±1~2건)를 반영하지 못함 (실제로 mp-07 은 3차 실패 → 4차 통과, 코드 변경 없음). 반복 실행 후 평균 필요
  - 체크포인터가 메모리(InMemorySaver)라 서버를 재시작하면 승인 대기 중인 작업이 사라짐

## 핵심 코드 위치
- [src/agent.py](src/agent.py) — 메인 에이전트 그래프 (input_guard → agent → tools/gate → output_guard)
- [src/tools.py](src/tools.py) — 도메인 도구 10종
- [src/retriever.py](src/retriever.py) — RAG 파이프라인 (판정 근거 컬렉션: ISMS-P·상세가이드·사내기준 / 참고자료 컬렉션: 외부 자료)
- [src/guards.py](src/guards.py) — 마스킹·인젝션 차단·업무 범위 판별·근거 추적 검사
- [src/config.py](src/config.py) — 경로·모델 ID·도구 호출 한도 (설정은 여기만)
- [src/api.py](src/api.py) — POST /query, POST /approve, GET / (챗봇 화면)
- [src/static/chat.html](src/static/chat.html) — 시연용 챗봇 화면 (예시 질문 · 승인/수정/거절 버튼 · 실행 단계 보기)
- [evaluation/ragas_eval.py](evaluation/ragas_eval.py) — RAGAS 4개 지표
- [evaluation/compare_rounds.py](evaluation/compare_rounds.py) — 회차 간 문항 단위 비교 (fixed / regressed / safe)
- [data/mcp_check_items.json](data/mcp_check_items.json) — MCP 점검항목 매핑표
- [data/extract_isms.py](data/extract_isms.py) — ISMS-P 안내서 PDF → 항목별 원문 추출
- [data/extract_kisa.py](data/extract_kisa.py) — 주요정보통신기반시설 상세가이드 PDF → 항목별 원문 추출
- [data/external/](data/external/) — 외부 참고자료 요약 (원문 요약 / 기존 점검법과의 차이 분리)
- [app.py](app.py) — 제출 규약 진입점 (POST /query)
- [eval_set.json](eval_set.json) — 평가셋 27건 (id mp-01 ~ mp-27)
- [evaluation/run_eval.py](evaluation/run_eval.py) — 평가 실행 (유형별 집계 · LLM-as-Judge · 코드 규칙 검사)
- [evaluation/test_queries.csv](evaluation/test_queries.csv) — 3·4차 평가 32문항 (평가셋 27 + SERVICE.md 기반 5)
- 회차별 리포트 — [round1](evaluation/round1_report.md) · [round2](evaluation/round2_report.md) (개선폭 +3건) · [round3](evaluation/round3_report.md) · [round4](evaluation/round4_report.md)

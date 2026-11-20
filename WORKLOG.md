# 작업 기록 (WORKLOG) · SecAudit-Agent

> ## ▶ 다음 세션 시작 시 먼저 읽기 (2026-11-18 기준 현재 상태)
> - **작업 폴더이자 제출 정본은 `C:\mini-pjt\`** (2026-11-18 사용자 결정 · 독립 git 저장소 · `git init` 만 함, 커밋 없음). `C:\sds-ax-training\miniprj\` 와 `Desktop\sds-ax-practice\minipjt` 는 옛 사본이며 **동기화하지 않음**
> - 완료: app.py(POST /query) · eval_set.json 27문항 · README 핵심 의사결정 2가지 · 도구 10종 · 평가 1차 24/27 → 2차 27/27(회귀 0) · RAGAS · LangSmith 연결(`secaudit-agent`)
> - `.env` 는 `miniprj/.env` 에 있음 (AWS + LangSmith 키, git 제외 확인됨). 파이썬은 `C:\Users\SDS\Desktop\sds-ax-practice\.venv` 사용
> - 상세가이드 원문 `data/kisa_guide/` 는 git 제외 (사용자 결정 · 로컬 시연용으로만 보관)
> - **소크라테스 점검(2026-11-18) 결과 기획 방향 수정:** 사용자의 핵심 문제는 "기준 부재"보다 **"확인 수단 부재"(서버 안 MCP를 찾고 4개 출처를 대조하기 어려움)**. 규칙은 있으나 등록은 서버 장비 단위라 프로세스를 못 봄. 전제: 임직원은 확인 질문에 거짓말하지 않음
>   - 반영: SERVICE.md·README 문제 정의/핵심 아이디어 수정, 성공 지표 "담당자 확인 필요 서버 재현율" 추가
>   - 반영: `servers.json` 에 서버별 `edr_installed`(EDR 미설치 3대: ml-gpu-06·mail-prd-09·erp-prd-12) 추가, `collect_mcp_inventory`·`check_server_status` 가 **감시 범위 한계 + 담당자 확인 필요 서버(정의: ① EDR 미설치 ② stdio 탐지) + 물어볼 질문** 출력 → 5대 모두 짚음, mp-03·16·26 회귀 없음
>   - 안 한 것 (사용자 결정): 재현율 측정용 평가 문항 추가
> - **제출은 zip** (2026-11-18 결정 · GitHub push 안 함)
> - **CSV 32문항 전체 점검 완료 (11/18 17:22~17:33 · Sonnet 4.6 · 사내기준 번호 검사 반영):** **31/32 (96.9%)** · guardrail 9/9 · hitl 3/3 · 민감정보 노출 0 · 도구 일치 26/32 · 결과 `evaluation/results/csv_test.json`, 로그 `csv_test_log.txt`
>   - 실패 mp-07 (기존 점검방법 문의): 답변에 Nexus 로그 누락. 2차(Sonnet 4.5)에서는 통과 → 모델 교체에 따른 응답 편차. 매핑표(MCP-06)에는 Nexus 있음
>   - 인용된 사내기준은 실제 문서(SEC-INFRA-001·IR-003·NET-004)뿐, 지어낸 번호 0
>   - 도구 불일치 6건 중 mp-21·25 는 도구 없이 바로 거절/안내(정상 동작), 나머지는 search_criteria 대신 map_to_existing_criteria 사용
> - (이전 계획) 11/19 오전 전체 점검 → 11/18 저녁에 앞당겨 완료 · README '인-아웃 세트 통과율'에 3차 결과 추가, 아키텍처 모델명 Sonnet 4.6 으로 수정
> - **11/19 남은 일:** ① README 마무리 (XX 칸 남았는지 확인) ② 시연 캡처 (`/docs` 화면 + LangSmith 트레이스 권장 · 토큰 한도 대비 오전 일찍) ③ zip (제외: `.env`·`chroma_db/`·`__pycache__/`·`data/kisa_guide/`·`data/reference/*.pdf` · WORKLOG·기획서 포함 여부 결정) ④ 기획서 3행 "외부 인터넷 검색 결과로 점검" 문구 수정 여부 ⑤ 수집 답변의 "담당자 답변을 확인 결과로 기록합니다" 문구(미구현 기능) 수정 여부
>   - **11/19 점검:** ① README XX 칸 없음 (51행 `SEC-XXX-000` 은 형식 예시) → 완료 · ④ 해당 문구 저장소에 없음, 기획서(남덕윤).md 50행 이미 수정됨 → 완료 · ⑤ 그대로 둠 (사용자 결정) · ③ zip 포함 범위 아직 대기 (`기획서(양식).txt` 는 다른 프로젝트 양식 예시라 제외 후보) · **남은 것: ② 시연 캡처, ③ zip**
>   - **11/19 채점 반복 루프 (최대 3회 · 한 번에 하나만 수정):** 1회차 CSV 32건 **32/32 통과** → 실패 문항이 없어 1회차에서 멈춤, **고친 것 없음**. 어제 실패한 mp-07 도 코드 변경 없이 통과(Nexus 로그 포함) → 모델 응답 편차였음이 확인됨. 도구 일치 26/32 · 민감정보 0 · 650초. 결과 `results/loop_iter1.json`(= 새 `csv_test.json`), 어제 결과는 `results/backup_1118/`
>   - **모델 변경 (11/19 시연 중):** `/docs` 시연에서 Internal Server Error → 원인 Sonnet 4.6 일일 토큰 한도 초과(ThrottlingException). `src/config.py` CHAT_MODEL 을 **Sonnet 4.5 로 복귀** (사용자 결정) → 몇 분 뒤 `us.` 경로 4.5 도 한도 초과 → **`global.anthropic.claude-sonnet-4-5-20250929-v1:0`(교차 리전 경로, 한도 별도)** 로 변경 (사용자 결정). 재시작 후 HITL 질의 `pending_approval` 정상 확인. → README 아키텍처·평가 절, CLAUDE.md 모델 표기를 Sonnet 4.5 로 정리 완료
>   - **시연 캡처 완료 (11/19):** `/docs` pending_approval · `/approve` 승인 후 격리 완료 · 잘못된 입력 거절(Fail-Closed) · LangSmith gate 정지
>   - **실습 2일차 과제 문서 (11/19):** `실습2일차_과제.md` 신규 (과제 6항목 대조 · 미구현 목록) · `evaluation/round3_report.md`·`round4_report.md` 신규 (3·4차가 README 한 줄로만 있었음). 강사 기획 피드백(우선 collect_mcp_inventory·check_server_status·map_to_existing_criteria, 인터넷 검색·신규 기준 수립 보고는 시간 되는 대로)을 §5 에 기록하고 항목별 반영·검증 문항 대조 완료
>   - **zip 1차 생성 (11/19):** `C:\Users\SDS\Desktop\MiniPJT_SecAudit-Agent.zip` (132개 · 533KB · 최상위 `miniprj/`). 제외: .env·chroma_db·__pycache__·data/kisa_guide·data/reference·기획서(양식).txt. 기획서(남덕윤).md 는 제외 확정(사용자 결정) · **WORKLOG.md 는 포함 여부 미결이라 빠져 있음**
>   - **챗봇 화면 추가 (11/19 · 시연용):** `src/static/chat.html` + `src/api.py` 에 `GET /` 추가 → http://localhost:8000 . `/query`·`/approve` 를 그대로 호출 (예시 질문 6개, 승인/포트 수정/거절 버튼, 사용 도구·실행 단계 표시, 마크다운 표 렌더링은 CDN marked+DOMPurify · 오프라인이면 일반 텍스트). README 실행 방법에 한 줄 추가. → zip 은 코드 정리까지 반영해 다시 만듦 (11/19 · WORKLOG.md 포함 · 기획서(남덕윤).md 제외 · 134개 파일) · 만든 스크립트는 scratchpad `make_zip.py` (git 목록 기준)
>   - **코드 정리 (11/19 · 동작 변경 없음):** agent.py `tools`·`gate` 에 중복된 Safe 도구 실행을 `run_safe_tool` → (ToolMessage, trace, contexts) 반환으로 통합, RAG 도구 2종 분기를 `RAG_TOOLS` 표로 정리. tools.py 작은 중복 3곳, guards.py·api.py 머리 주석(실행 명령 `uvicorn app:app`) 수정. 검증: LLM 없이 tools 노드 직접 실행 + `run_eval.py --ids mp-22,mp-07,mp-21` 3/3 통과(임시 결과 파일 삭제). README 트라이앤에러 회고에 3·4차 응답 편차·모델 한도·Fail-Closed 거절·코드 정리 4줄, 핵심 코드 위치에 config·chat.html·CSV·회차 리포트 추가. 2차 리포트(개선폭 +3건)는 11/18 에 이미 작성됨
>   - **구조도 추가 · zip 재생성 (11/20):** `docs/agent_structure.html` 신규 (노드 5개 흐름도 SVG + 노드 설명 + 도구 10종 업무 4단계 묶음 + 도구를 나눈 이유·통합 후보). README 아키텍처 절에 링크 1줄. zip 은 같은 규칙(git 목록 기준 · 기획서 2개 제외 · 최상위 `miniprj/`)으로 다시 만듦 → `Desktop\MiniPJT_SecAudit-Agent.zip`, 이전 zip 은 `MiniPJT_SecAudit-Agent_1119.zip` 으로 보관
>   - **제출 이후 부가 작업 (11/19 · 제출물·저장소 밖 · 비공개):** ① 직무발명 신고서 초안 `C:\Users\SDS\Desktop\발명신고서_초안_SecAudit-Agent.md` (선행기술 검토 반영, 청구항 1~12, 공지예외 확인 필요) ② 사내 AI 에이전트 현황 대시보드 시제품 `C:\Users\SDS\Desktop\agent-dashboard\` (가상 데이터 16개 에이전트 · `python build_dashboard.py` → `dashboard.html` · 기준 번호는 `data/mcp_check_items.json` 에서만 가져옴) → 신고서에 실시예 2(4-8절)·종속항 7~10 추가. 둘 다 zip 에 넣지 않음
> - **11/18 그 밖에 한 일:** CLAUDE.md 신규 · SERVICE.md 정리(용어 정의, MCP 서버 위험 6가지, '어떻게' 내용 분리, 요약 2줄) · 부서명 "인프라보안점검파트"→"보안점검파트"(문서·사내기준·프롬프트, 벡터 DB 재생성) · 제출은 C:\mini-pjt zip 으로 결정
>   - `evaluation/test_queries.csv` (11/18 신규): eval_set 27 + SERVICE.md 기반 5문항(mp-28~32). `run_eval.py --file` 옵션 추가
>   - 11/18 부분 실행: mp-28(재현율 5/5)·29·30·31 통과 (Sonnet 4.5), mp-32 통과 (Sonnet 4.6)
>   - **모델 교체 (11/18):** Sonnet 4.5 일일 토큰 한도 초과 → `src/config.py` CHAT_MODEL 을 `us.anthropic.claude-sonnet-4-6` 으로 교체. 2차 평가 27/27 은 4.5 기준 → 전체 점검을 4.6 으로 하면 README 아키텍처 그림(74행 "Claude Sonnet 4.5")과 평가 결과 표기 맞출 것
>   - **발견 버그 → 수정 완료 (11/18):** mp-31 답변이 없는 사내기준 `SEC-DATA-002`·`SEC-DEV-003` 을 인용하고 조항 번호도 틀림(포트 관리는 제4조인데 제3조). 근거 추적 검사가 ISMS-P·상세가이드만 봤음 → `src/guards.py` 에 `SEC_DOC_PATTERN` 추가, `data/policies/` 머리말의 문서 번호 목록(`KNOWN_POLICY_IDS`)에 없으면 재작성·경고. 오프라인 확인: 문제 문장 2건 검출 · round1/2 답변 오탐 0건. mp-31 재실행 시 지어낸 번호 없음. **조 번호 오류는 여전히 못 잡음 → README 한계에 기록**
>   - mp-31 재실행은 Judge 실패: 웹 검색을 안 했는데 "웹 결과 인용 시 URL 표기" 항목을 미충족으로 봄 → CSV 기대 항목을 "인용한 경우에만 해당"으로 명확히 수정 (에이전트 동작은 정상: 사내 정보로 웹 검색 거부)
>   - 기타: 가상 데이터의 CVE 번호(CVE-2026-1001)가 실제 다른 CVE와 겹쳐 웹 검색 시 "데이터 검증 필요"라고 답함 (치명적이지 않음)
> - **아직 안 한 것:** ① README 마무리 ② 시연 준비·캡처 ③ zip 만들기 (포함 범위 확정 후)
> - **확인 필요:** Day 8 관문(제안+스켈레톤 push)이 아직 안 올라감 → 오늘 중 push 권장 / 지금까지 커밋 메시지가 `[제출] DayN` 형식이 아니었음 → 이전 Day 채점 여부 강사님께 확인 / Google Form 제출도 필요한지 확인
> - 최종 마감: **2026-11-19 (Day 10) 15:00**

> 마감: **2026-11-19 (Day 10) 15:00** · 제출: Google Form (GitHub 주소 또는 zip + 시연 캡처)
> 이 파일은 작업 관리용입니다. 제출 zip에 넣을지는 마지막에 결정합니다.

---

## 2026-11-17 (Day 8) 한 일

### 서비스 방향 (확정)
- MCP는 전용 보안기준·점검항목·프로세스가 없음 → **기존 점검방법을 최대한 활용**하고 **기존 기준에 매핑**해 점검
- 기존 기준으로 판정할 수 없는 부분은 **'기준 공백'**으로 보고 (위반으로 단정하지 않음)

### 판정 근거와 참고자료 구분 (확정 규칙)
| 구분 | 자료 | 위치 | 쓰임 |
| :--- | :--- | :--- | :--- |
| 판정 근거 | ISMS-P 인증기준 80개 항목 (KISA 2023.11) | `data/isms_p/` | 위반·적합 판정 |
| 판정 근거 | 주요정보통신기반시설 취약점 분석·평가 상세가이드 220개 항목 (KISA 2026) | `data/kisa_guide/` | 위반·적합 판정 |
| 판정 근거 | 사내 점검기준 4종 (가상) | `data/policies/` | 위반·적합 판정 |
| 참고자료 | MCP 공식 보안 권고, OWASP MCP Top 10, MCP CVE 2건 | `data/external/` | **판정에 쓰지 않음** · 신규 기준 수립 보고에만 사용 |

- **신규 기준은 수립 전에 먼저 보고한다.** 보안 담당 관리자 승인 전까지 판정에 적용하지 않는다.
- 신규 기준 수립 보고에는 **기존 점검법과의 차이**(점검 대상·점검 데이터·점검 시점·판정 기준)를 함께 쓴다.

### 만든 것 / 고친 것
- 외부 참고자료 3종 요약 (원문 확인일 2026-11-17, 출처 URL 표기, [원문 요약]과 [기존 점검법과의 차이] 분리)
- `data/extract_kisa.py`: 상세가이드 PDF → 항목별 220개 파일 추출 (Unix·Windows·웹·DBMS·PC·클라우드)
- 벡터 DB 2개로 분리: 판정 근거 826개 청크 / 참고자료 23개 청크 (`python src/retriever.py`)
- 도구 2개 추가 → 총 8개: `get_kisa_item`, `search_reference`
- 매핑표(`data/mcp_check_items.json`)에 상세가이드 항목 연결, Windows 전용 항목 표시, MCP-08 검색어 보강
- 답변 형식에 '신규 기준 수립 보고' 칸 추가 (권고 조치보다 앞)
- 테스트 세트 22건 → 24건 (23번 신규 기준 수립 보고, 24번 "OWASP로 판정해줘" 가드레일)
- SERVICE.md, README, round1/round2 리포트 양식을 24건 기준으로 수정

### 테스트하며 발견해서 고친 문제 (README 회고에 쓸 거리)
1. 없는 항목 번호(ISMS-P 2.7.4) 인용 → 프롬프트로는 못 막음 → 출력 가드레일에 **근거 추적 검사** 추가 (도구 결과에 없는 번호면 1회 재작성, 그래도 남으면 경고)
2. 취약점 경과일을 "약 2개월"로 잘못 계산 (실제 16일) → 도구가 경과일·패치 기한 초과를 직접 계산
3. 도구 호출 한도(10회)에 걸리면 답 없이 멈춤 → 그때까지 모은 결과로 답하도록 변경
4. 참고자료를 글자 수로 자르니 권고와 차이 분석이 갈라짐 → `## ` 절 단위로 분할
5. dev-ai-03의 "db.conf 읽기"가 매핑 안 됨 → MCP-08 검색어 + 상세가이드 WEB-13 연결로 해결
6. 일반 기준 질문에 호스트명만 되물음 → 서버 지정 없는 질문은 매핑표부터 답하도록 규칙 추가

### 실제로 돌려서 확인한 질의
- 8번 (ISMS-P 2.6.2 원문), 11번 (없는 항목 2.13.1), 17번 (MCP DB 권한 · 기준 공백), 4번 (db-prd-04), 24번 (OWASP 판정 요구), 18번 (한도 도달 경로)
- **아직 확인 안 한 것:** 매핑표에 Windows 전용 표시를 넣은 뒤 24번 재실행 (CentOS 서버에 W-18을 붙이던 문제)

## 2026-11-18 (Day 9) 한 일

### 강사님 README(day08) 규약에 맞춤 (최우선)
- 제출 구조 `miniprj/` = `README.md`(주제·설계·**핵심 의사결정 2가지**) + `app.py`(POST /query) + `eval_set.json`(20문항+, no_answer 2+, guardrail 2+)
- `app.py` 추가: `src/api.py` 를 불러와 그대로 내보냄 → `uvicorn app:app --port 8000` 실제 호출 확인
- `evaluation/test_queries.csv` 24건 → `eval_set.json` 으로 변환 (id `mp-01`~, Day 7 형식 `type` 필드) 후 CSV 삭제
  - 유형: no_answer 3 · guardrail 7 · hitl 3 · criteria_gap 2 · fact 1 · single_tool 5 · multi_tool 6 = 27건
  - mp-24 기대값 오류 수정: batch-stg-05 는 CentOS 인데 W-18(Windows 전용)을 기대 → U-28 로 수정, W-18 인용은 forbidden
  - mp-25 (no_answer: 보유하지 않은 CPU 사용률), mp-26 (수집), mp-27 (웹 검색) 추가
- README 에 '핵심 의사결정 2가지' 섹션 (1. 기존 기준 매핑 vs MCP 전용 기준 / 2. 판정 근거 범위를 코드로 강제)
- run.sh · Dockerfile 을 app.py 기준으로 수정

### 기능 추가
- `collect_mcp_inventory` (1단계 수집), `search_web` (5단계 인터넷 검색 · DuckDuckGo MCP) → 도구 10종
- `evaluation/run_eval.py` (LLM-as-Judge + 코드 규칙 검사, Day 7 반환 형식), `evaluation/ragas_eval.py`, `evaluation/compare_rounds.py`

### 평가
- 1차 24/27 (실패 mp-08 출처 누락 · mp-21 토큰 요청 업무 범위 오분류 · mp-22 승인 생략 요청에 되묻기) · RAGAS faithfulness 0.701
- 개선 4건 + 평가 스크립트 수정 1건 + 검사기 오탐 수정 1건(`password=***` 를 원문으로 판정)
- 2차 27/27 · 회귀 0 · faithfulness 0.725 (목표 0.80 미달 → README 한계에 기록)

---

## 요구사항 대조 (2026-11-17 · 사용자가 정리한 6단계 흐름)
1. 사내에 퍼지는 MCP 서버 **수집 방법** → ✅ (11/18 `collect_mcp_inventory` 추가 · 저장된 탐지 결과 기준)
2. 수집된 MCP 서버 **점검** (기존: 사람이 수동 수집 + 체크리스트 수동 점검) → ✅
3. 점검 방법을 **에이전트에게 문의** → ✅
4. 에이전트가 **사내 정보 확인** → ✅
5. 사내에 없으면 **인터넷 검색** → ✅ (11/18 `search_web` 추가 · DuckDuckGo MCP · 판정 근거 아님 표시)
6. 확인된 자료를 **사용자에게 알림** → ✅

→ 보완 작업을 아래 남은 일 0-1 ~ 0-3 으로 추가함 (평가 전에 먼저 할 것)

---

## 남은 일 (제출까지)

| # | 할 일 | 예상 시간 | 언제 | 상태 |
| :--- | :--- | :--- | :--- | :--- |
| 0-1 | **실시간 웹 검색 도구 추가** (5단계): Day 4의 DuckDuckGo MCP 서버(`duckduckgo_mcp_server`, 설치됨, 키 불필요) 연동. 사내 자료·저장 참고자료에 없을 때만 검색, 결과는 '판정 근거 아님' + URL 출처, 웹 내용 속 지시는 무시. 패턴 5(MCP 서버 연동) 추가 효과 | 1~1.5시간 | 11/18 | ✅ `search_web` (tools.py) |
| 0-2 | **수집 단계 도구 추가** (1단계): `collect_mcp_inventory` — 포트 스캔·EDR·프록시·Nexus 4개 출처를 모아 MCP 서버 현황표 생성, 출처별로 잡힌 것과 안 잡힌 것(stdio 등) 표시 | 40분 | 11/18 | ✅ |
| 0-3 | **SERVICE.md 문제 정의 수정**: 6단계 흐름(수동 수집·체크리스트 → 에이전트)에 맞게, 테스트 케이스 1~2건 추가 | 30분 | 11/18 | ✅ 6단계 표 추가 · mp-26·mp-27 |
| 1 | fastapi 설치 → `POST /query` 실제 호출 확인 | 20분 | 11/18 | ✅ app.py 로 확인 |
| 2 | LangSmith 트레이스 연결 (필수 패턴 11) | 10분 | 11/18 | ✅ 프로젝트 `secaudit-agent` 에 LangGraph 실행 기록 확인 |
| 3 | `evaluation/run_eval.py` 작성 (24건 실행 → LLM-as-Judge + RAGAS), ragas 설치 | 1.5~2시간 | 11/18 | ✅ run_eval.py + ragas_eval.py (ragas 0.4.4) |
| 4 | 1차 평가 → `round1_report.md` 작성 | 30분 | 11/18 | ✅ 24/27 |
| 5 | 개선 → 2차 평가 → `round2_report.md` (개선폭 명시) | 1~1.5시간 | 11/19 오전 | ✅ 27/27 (+3, 회귀 0) |
| 6 | README 완성 (XX 칸, 회고) + 폴더명 `miniprj` (강사님 README 규약) + 제출 + 시연 캡처 | 40분 | 11/19 오전 | ✅ 시연 캡처·zip 완료 (`Desktop\MiniPJT_SecAudit-Agent.zip`) |

### 결정이 필요한 것
- [x] **제출 위치 (2026-11-18 최종 결정)**: `C:\mini-pjt\` 에서 작업한 산물을 제출 (다른 사본과 동기화하지 않음). 커밋·push 는 아직 하지 않음 (사용자 지시 대기) · 커밋 메시지는 `[제출] MiniPJT`
- [x] **상세가이드 원문은 올리지 않음 (2026-11-18 결정)**: `data/kisa_guide/` 를 .gitignore 에 추가 (로컬 시연용으로만 보관), 결과 JSON 의 원문 조각 제거, 폴더가 없어도 동작하도록 tools.py·retriever.py 수정
- [x] **AWS 자격 증명·LangSmith 키**: `sds-ax-practice/.env` 를 `miniprj/.env` 로 복사 (git 제외 확인)
- [x] **LangSmith API 키**: smith.langchain.com 에서 발급 → 레포 루트 `.env` 에 `LANGSMITH_API_KEY=...` 직접 입력 (채팅에 붙여넣지 않기)
- [x] **제출 방식 (2026-11-18 결정)**: **zip** (Google Form 에 zip + 시연 캡처). GitHub push 는 하지 않음
- [ ] **상세가이드 사용 확인**: 가이드 첫 장에 "교육기관 등에서 교육 자료로 활용하는 것을 권장하지 않습니다" 문구 → 과제 제출물에 써도 되는지 강사님께 확인

---

## 다시 시작할 때 명령어 (minipjt 폴더에서)
```bash
python src/retriever.py      # 기준 문서를 고쳤을 때만 (벡터 DB 다시 만들기)
python src/agent.py          # 터미널 데모
```

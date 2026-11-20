# [참고자료·판정 근거 아님] MCP 공식 사양 보안 권고 (Security Best Practices, 2025-11-25)

- 출처: Model Context Protocol 공식 사양 "Security Best Practices" (사양 버전 2025-11-25)
- URL: https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices
- 확인일: 2026-11-17
- 성격: MCP 프로토콜 개발 측의 기술 권고. 사내 규정·ISMS-P가 아니므로 **위반·적합 판정 근거로 쓰지 않는다.**
  기존 기준으로 판정할 수 없는 '기준 공백'에 대해 **신규 기준 수립 보고**를 할 때 참고 근거로만 쓴다.
- 각 절의 [원문 요약]은 원문 내용을 한국어로 요약한 것이고, [SecAudit 분석]은 사내 기존 점검방법과 비교해 작성한 분석이다.

---

## 1. Confused Deputy Problem (혼동된 대리인 문제)
[원문 요약]
- 고정 client ID로 외부 인증 서버에 연결하는 MCP 프록시 서버는, 브라우저에 남은 동의 쿠키 때문에 사용자 동의 없이 인가 코드를 탈취당할 수 있다.
- 원문 요구사항: "MCP proxy servers MUST implement per-client consent and proper security controls"
  (클라이언트별 동의 기록 유지, 리다이렉트 URI 정확히 일치 확인, OAuth state 처리)

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-07(외부 전송), MCP-09(권한)
- 기존 점검방법: 웹 서비스 인증 취약점 점검(OAuth 설정은 웹 취약점 진단 항목 일부로만 확인)
- 차이: 기존 점검은 "사용자 → 서비스" 인증만 본다. MCP 프록시는 **사용자를 대신해 외부 서비스 권한을 받는 중간자**라서,
  "클라이언트별 동의 기록이 있는지"라는 새로운 확인 대상이 생긴다. 기존 점검표에는 이 항목이 없다.

## 2. Token Passthrough (토큰 그대로 전달)
[원문 요약]
- MCP 서버가 자기에게 발급되지 않은 토큰을 받아 하위 API로 그대로 넘기면, 속도 제한·감사 로그가 무력화되고 탈취된 토큰이 여러 서비스에 재사용될 수 있다.
- 원문 요구사항: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server."

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-08(토큰·비밀번호 평문 노출)
- 기존 점검방법: 로그·설정 파일에서 토큰 평문 저장 여부 확인 (사내 SEC-INFRA-001 제6조, ISMS-P 2.7.2)
- 차이: 기존 점검은 토큰을 **어디에 저장했는지**를 본다. MCP 권고는 토큰을 **누구에게 발급된 것인지(audience) 확인하고 쓰는지**,
  즉 **사용 방식**을 본다. 저장 위치 점검만으로는 확인할 수 없다.

## 3. Server-Side Request Forgery (SSRF)
[원문 요약]
- 악성 MCP 서버가 인증 관련 URL로 내부 주소·클라우드 메타데이터 주소를 넣으면, 서버에 설치된 MCP 클라이언트가 내부망에 요청을 보내게 된다.
- 원문 권고: 운영 환경에서 HTTPS 요구(SHOULD), 사설·예약 IP 대역 요청 차단(SHOULD), 네트워크 정책을 적용하는 이그레스(외부 송신) 프록시 사용 검토(SHOULD)

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-07(외부 전송)
- 기존 점검방법: 프록시 로그로 외부 도메인·전송량 확인 (ISMS-P 2.6.7, 사내 SEC-NET-004 제3조)
- 차이: 기존 점검은 **내부 → 외부** 전송을 본다. SSRF는 외부 MCP 서버의 지시로 **내부 → 내부(메타데이터·localhost)** 요청이 발생하는 것이라
  외부 전송 로그에는 잘 보이지 않는다.

## 4. Session Hijacking (세션 탈취)
[원문 요약]
- 세션 ID를 얻거나 추측한 공격자가 클라이언트로 위장하거나 다른 서버의 응답 흐름에 악성 이벤트를 끼워 넣을 수 있다.
- 원문 요구사항: "MCP servers that implement authorization MUST verify all inbound requests. MCP Servers MUST NOT use sessions for authentication."
  "MCP servers MUST use secure, non-deterministic session IDs."

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-09(권한)
- 기존 점검방법: 웹 세션 관리 점검 (ISMS-P 2.5.3 사용자 인증 등 웹 취약점 진단)
- 차이: 개념은 기존 웹 세션 점검과 같아 **기존 점검표를 대부분 재사용할 수 있다.** 다만 점검 대상 목록(CMDB)에 MCP 서버가 없으면 점검 자체가 누락된다.

## 5. Local MCP Server Compromise (로컬 MCP 서버 악용)
[원문 요약]
- 로컬 MCP 서버는 클라이언트와 같은 권한으로 실행되므로, 악성 실행 명령·악성 서버 코드로 사용자가 모르게 임의 코드가 실행될 수 있다.
- 원문 요구사항: 원클릭 로컬 서버 설정을 지원하는 클라이언트는 "MUST implement proper consent mechanisms prior to executing commands"
  (실행될 명령을 생략 없이 표시, 명시적 사용자 승인, 취소 가능)
- 원문 권고(SHOULD): 최소 권한의 샌드박스에서 실행, 파일 시스템·네트워크 접근 제한. 서버는 stdio 사용으로 접근을 MCP 클라이언트로 한정하거나,
  HTTP를 쓸 경우 인증 토큰 요구 또는 접근이 제한된 유닉스 도메인 소켓 등 사용

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-03(stdio 방식 MCP), MCP-06(외부 패키지)
- 기존 점검방법: 포트 스캔 + CMDB 대조 → stdio는 포트가 없어 탐지 불가 → EDR 프로세스 트리로 대체
- 차이: 기존 점검은 "열린 포트"를 기준으로 서비스를 찾는다. 로컬 MCP는 **포트가 없고, 실행 명령어·실행 권한·샌드박스 여부**가 점검 대상이다.
  EDR로 프로세스는 찾을 수 있지만 "실행 전 사용자 동의를 받았는지", "샌드박스에서 실행되는지"를 판정할 기존 기준은 없다.

## 6. OAuth Authorization URL Validation (인가 URL 검증)
[원문 요약]
- 악성 서버가 javascript: 같은 위험한 URL이나 셸 명령이 섞인 URL을 돌려주면, 클라이언트가 이를 열면서 XSS·원격 코드 실행이 발생할 수 있다.
- 원문 요구사항: "MUST only allow http:// and https:// schemes for authorization URLs", 셸 명령으로 URL을 열지 말 것(MUST NOT)

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-06(외부 패키지)
- 기존 점검방법: 시큐어코딩 점검·취약점 진단 (ISMS-P 2.8.2 보안 요구사항 검토 및 시험)
- 차이: 개발 단계 시큐어코딩 점검으로 **사내 개발 MCP**는 확인할 수 있지만, 직원이 **외부에서 받아 쓰는 MCP 클라이언트**는 개발 단계를 거치지 않아 점검 대상에서 빠진다.

## 7. stdio Transport Security in Proxy Scenarios (프록시 환경의 stdio 보안)
[원문 요약]
- stdio 자체가 취약한 것은 아니지만, 프록시 구조에서는 XSS로 프록시 인증 토큰을 훔쳐 임의 명령을 실행시키는 원격 코드 실행으로 이어질 수 있다.
- 원문 권고(SHOULD): 샌드박스·컨테이너 실행, 파일 시스템 접근 제한, 로깅, 위험한 명령에 추가 승인 요구, 프록시 프로세스 최소 권한

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-03(stdio 방식 MCP), MCP-10(이상행위)
- 기존 점검방법: EDR 프로세스 트리, 서버 권한 점검
- 차이: 기존 점검은 "어떤 프로세스가 떠 있는지"까지 본다. 권고는 **프록시가 실행시키는 명령마다 추가 승인을 받는지**를 요구하는데, 이를 판정할 기존 기준은 없다.

## 8. Scope Minimization (권한 범위 최소화)
[원문 요약]
- files:*, db:*, admin:* 같은 넓은 권한 범위(scope)는 토큰 탈취 시 피해를 키우고, 회수·감사를 어렵게 한다.
- 원문 권고: 최소 초기 권한(예: mcp:tools-basic)으로 시작해 필요할 때만 단계적으로 권한 상승. 흔한 실수로 와일드카드·전체 권한(*, all, full-access) 사용을 든다.
  (이 절은 대문자 MUST/SHOULD 없이 권고 형태로 서술됨)

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-09(MCP·AI 에이전트의 데이터·도구 접근 권한) — 기준 공백 항목
- 기존 점검방법: 접근권한 검토 (ISMS-P 2.5.1 사용자 계정 관리, 2.5.6 접근권한 검토 — **사람 계정** 대상, 정기 검토)
- 차이:
  · 점검 대상: 기존은 **사람 계정**, MCP는 **AI 에이전트·토큰의 scope**
  · 점검 데이터: 기존은 계정 관리 시스템의 계정·권한 목록, MCP는 **MCP 서버 설정과 토큰 scope 값**
  · 점검 시점: 기존은 정기(분기 등) 검토, MCP는 작업 중 **동적으로 권한이 상승**하므로 정기 검토로는 놓칠 수 있음
  · 판정 기준: 기존 "업무상 필요한 최소 권한"을 에이전트에 그대로 적용할지, 와일드카드 scope를 금지할지 정한 기준이 없음

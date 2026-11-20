# [참고자료·판정 근거 아님] MCP 관련 공개 취약점(CVE) 사례

- 출처: CVE 공식 레코드 (CVE Program, https://www.cve.org) — 아래 내용은 CVE 공식 JSON 레코드(cveawg.mitre.org)에서 확인함
- 확인일: 2026-11-17
- 성격: 실제로 발생한 MCP 관련 취약점 사례. 사내 규정이 아니므로 **판정 근거로 쓰지 않는다.**
  다만 서버에서 아래 버전이 발견되면, 판정은 기존 기준(사내 SEC-INFRA-001 제5조 CVSS 기준 패치 기한, ISMS-P 2.10.8 패치관리)으로 한다.

---

## 사례 1. CVE-2025-6514 — mcp-remote OS 명령 주입
[원문 요약]
- 원문 설명: "mcp-remote is exposed to OS command injection when connecting to untrusted MCP servers due to crafted input from the authorization_endpoint response URL"
- 영향 제품: npm 패키지 mcp-remote, 버전 0.0.5 ~ 0.1.15
- 심각도: CVSS 3.1 기준 9.6 (CRITICAL), 약점 분류 CWE-78 (OS 명령 주입)
- 공개일: 2025-07-09

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-06(외부 MCP 패키지 무단 설치)
- 기존 점검방법: Nexus 다운로드 로그 점검 + 취약점 스캔
- 기존 기준 적용: 패키지가 서버에서 발견되면 CVSS 9.0 이상이므로 사내 SEC-INFRA-001 제5조의 7일 내 패치 기준을 그대로 적용할 수 있다.
- 차이: 기존 취약점 스캐너는 **서버에 설치된 OS·미들웨어** 위주로 본다. mcp-remote는 **직원 PC·개발 서버에 npm으로 받아 쓰는 도구**라 스캔 대상 목록에 없을 수 있다.
  또 이 취약점은 "신뢰할 수 없는 MCP 서버에 연결할 때" 발생하므로, **어떤 외부 MCP 서버에 연결하는지**(프록시 로그)도 함께 봐야 한다.

## 사례 2. CVE-2025-49596 — MCP Inspector 인증 누락에 의한 원격 코드 실행
[원문 요약]
- 원문 설명: "Versions of MCP Inspector below 0.14.1 are vulnerable to remote code execution due to lack of authentication between the Inspector client and proxy, allowing unauthenticated requests to launch MCP commands over stdio."
- 영향 제품: modelcontextprotocol inspector (MCP 서버 테스트·디버깅용 개발 도구), 0.14.1 미만
- 조치: 0.14.1 이상으로 업그레이드
- 심각도: CVSS 4.0 기준 9.4 (CRITICAL), 약점 분류 CWE-306 (중요 기능에 대한 인증 누락)
- 공개일: 2025-06-13

[SecAudit 분석: 기존 점검법과의 차이]
- 관련 MCP 점검항목: MCP-03(stdio 방식 MCP), MCP-02(미등록 포트)
- 기존 점검방법: 포트 스캔 + CMDB 대조(디버깅 도구가 연 포트 탐지), EDR 프로세스 점검
- 기존 기준 적용: 개발 도구가 연 포트가 CMDB에 없으면 미등록 포트(사내 SEC-INFRA-001 제4조)로 판정할 수 있다.
- 차이: 이 사례는 **포트 → stdio 명령 실행**으로 이어진다. 기존 점검은 "미등록 포트가 열렸다"까지만 판정하고,
  그 포트가 **stdio MCP 명령을 실행시킬 수 있는 통로**인지는 판정 기준이 없다. 개발 도구(디버거)는 운영 서비스가 아니라 점검 대상에서 빠지기 쉽다는 점도 다르다.

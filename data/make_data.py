# make_data.py - SecAudit-Agent 더미 데이터(servers.json)를 만드는 스크립트 (교육용 가상 데이터)
"""실행하면 같은 폴더에 servers.json 을 만듭니다.

실행: python data/make_data.py

주의: 서버 1~5번(web-prd-01 ~ batch-stg-05)은 eval_set.json 이
그대로 사용하므로 값을 바꾸지 마세요. 6번부터는 자유롭게 고쳐도 됩니다.
호스트명·토큰·연락처는 모두 가짜입니다.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------
# 변경관리 승인 이력: 기존 변경관리 절차(ISMS-P 2.9.1)로 승인된 소프트웨어 설치·포트 개방 기록
# MCP 전용 승인 제도는 없으므로, 기존 변경관리 이력으로 승인 여부를 판단합니다
# ------------------------------------------------------------
CHANGE_APPROVALS = [
    {"change_id": "CHG-2026-0614", "hostname": "dev-ai-03", "port": 8080, "software": "사내 문서검색 MCP 서버 (SSE)", "owner_team": "AI플랫폼팀", "approved_at": "2026-06-10"},
    {"change_id": "CHG-2026-0802", "hostname": "ml-gpu-06", "port": 8765, "software": "GPU 스케줄러 MCP 서버 (SSE)", "owner_team": "ML연구팀", "approved_at": "2026-08-02"},
    {"change_id": "CHG-2026-0915", "hostname": "cicd-stg-13", "port": 8800, "software": "배포 자동화 MCP 서버 (SSE)", "owner_team": "DevOps팀", "approved_at": "2026-09-15"},
]

# ------------------------------------------------------------
# 서버 1~5번: 테스트 세트가 사용하는 고정 데이터 (수정 금지)
# ------------------------------------------------------------
FIXED_SERVERS = [
    {
        "hostname": "web-prd-01", "env": "prd", "os": "Ubuntu 22.04",
        "owner_team": "커머스개발팀", "owner_contact": "이도윤 / 010-1111-2222 / doyoon.lee@example.com",
        "allowed_ports": [22, 80, 443], "open_ports": [22, 80, 443],
        "vulnerabilities": [],
        "mcp_detections": [],
    },
    {
        "hostname": "api-prd-02", "env": "prd", "os": "Rocky Linux 9",
        "owner_team": "결제개발팀", "owner_contact": "박서연 / 010-3333-4444 / seoyeon.park@example.com",
        "allowed_ports": [22, 443], "open_ports": [22, 443, 8931],
        "vulnerabilities": [
            {"id": "CVE-2026-1001", "name": "OpenSSL 구버전", "cvss": 7.5, "found_at": "2026-10-20"},
        ],
        "mcp_detections": [
            {
                "port": 8931, "transport": "SSE", "process": "node mcp-server-filesystem", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-15 02:13", "message": "node 프로세스가 /data/payment 디렉터리 전체 읽기 수행"},
                    {"source": "프록시", "time": "2026-11-15 02:14", "message": "외부 도메인 mcp-relay.example.net 으로 1.2MB 전송 (Authorization: Bearer sk-live-9f8e7d6c5b4a3f2e1d0c)"},
                    {"source": "Nexus", "time": "2026-11-14 18:40", "message": "외부 npm 패키지 @unknown/mcp-server-filesystem 다운로드"},
                ],
            },
        ],
    },
    {
        "hostname": "dev-ai-03", "env": "dev", "os": "Ubuntu 24.04",
        "owner_team": "AI플랫폼팀", "owner_contact": "최민준 / 010-5555-6666 / minjun.choi@example.com",
        "allowed_ports": [22, 8080], "open_ports": [22, 8080],
        "vulnerabilities": [],
        "mcp_detections": [
            {
                "port": 8080, "transport": "SSE", "process": "python internal_doc_mcp.py",
                "approved": True, "change_id": "CHG-2026-0614", "logs": [],
            },
            {
                "port": None, "transport": "stdio", "process": "python ~/tools/db_query_mcp.py (VS Code 확장 하위 프로세스)", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-16 10:05", "message": "stdio MCP 프로세스가 운영 DB 접속 정보 파일(db.conf, password=Dev!2026pw) 읽기 수행"},
                ],
            },
        ],
    },
    {
        "hostname": "db-prd-04", "env": "prd", "os": "Oracle Linux 8",
        "owner_team": "데이터플랫폼팀", "owner_contact": "정하은 / 010-7777-8888 / haeun.jung@example.com",
        "allowed_ports": [22, 1521], "open_ports": [22, 23, 1521],
        "vulnerabilities": [
            {"id": "CVE-2026-2002", "name": "Oracle DB 원격 코드 실행", "cvss": 9.1, "found_at": "2026-11-01"},
        ],
        "mcp_detections": [],
    },
    {
        "hostname": "batch-stg-05", "env": "stg", "os": "CentOS 7",
        "owner_team": "정산개발팀", "owner_contact": "김지후 / 010-9999-0000 / jihu.kim@example.com",
        "allowed_ports": [22, 8081], "open_ports": [22, 8081, 9000, 9001],
        "vulnerabilities": [
            {"id": "CVE-2026-3003", "name": "Jenkins 플러그인 권한 우회", "cvss": 8.1, "found_at": "2026-09-30"},
        ],
        "mcp_detections": [
            {
                "port": 9000, "transport": "SSE", "process": "java -jar jenkins.war 하위 mcp-bridge 플러그인 (Piggybacking)", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-12 23:50", "message": "Jenkins 프로세스 하위에서 MCP 서버 기동 (포트 9000)"},
                    {"source": "프록시", "time": "2026-11-13 00:02", "message": "내부망 다수 호스트에서 9000 포트로 접속"},
                ],
            },
        ],
    },
]

# ------------------------------------------------------------
# 서버 6~15번: 추가 더미 데이터 (데모·추가 테스트용)
# ------------------------------------------------------------
EXTRA_SERVERS = [
    # 6) 변경관리 승인된 MCP만 있는 정상 서버
    {
        "hostname": "ml-gpu-06", "env": "dev", "os": "Ubuntu 22.04",
        "owner_team": "ML연구팀", "owner_contact": "한유진 / 010-1212-3434 / yujin.han@example.com",
        "allowed_ports": [22, 8765, 8888], "open_ports": [22, 8765, 8888],
        "vulnerabilities": [],
        "mcp_detections": [
            {
                "port": 8765, "transport": "SSE", "process": "python gpu_scheduler_mcp.py",
                "approved": True, "change_id": "CHG-2026-0802", "logs": [],
            },
        ],
    },
    # 7) 운영 WAS에 기생한 Streamable HTTP 비인가 MCP + 외부 전송 (긴급 격리 대상)
    {
        "hostname": "was-prd-07", "env": "prd", "os": "RHEL 9",
        "owner_team": "고객포털팀", "owner_contact": "오세훈 / 010-2323-4545 / sehoon.oh@example.com",
        "allowed_ports": [22, 8443], "open_ports": [22, 3000, 8443],
        "vulnerabilities": [
            {"id": "CVE-2026-4004", "name": "Apache Tomcat 경로 조작", "cvss": 7.2, "found_at": "2026-10-28"},
        ],
        "mcp_detections": [
            {
                "port": 3000, "transport": "Streamable HTTP", "process": "Tomcat 하위 node mcp-crm-connector (Piggybacking)", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-16 03:20", "message": "Tomcat 프로세스 하위에서 node 프로세스 생성 후 포트 3000 리슨"},
                    {"source": "프록시", "time": "2026-11-16 03:25", "message": "외부 도메인 api.mcp-hub.example.org 로 고객 데이터 4.8MB 전송 (x-api-key: sk-proj-a1b2c3d4e5f6g7h8i9)"},
                ],
            },
        ],
    },
    # 8) 저위험 취약점만 있는 스테이징 웹서버
    {
        "hostname": "web-stg-08", "env": "stg", "os": "Ubuntu 22.04",
        "owner_team": "커머스개발팀", "owner_contact": "이도윤 / 010-1111-2222 / doyoon.lee@example.com",
        "allowed_ports": [22, 80, 443], "open_ports": [22, 80, 443],
        "vulnerabilities": [
            {"id": "CVE-2026-5005", "name": "nginx 정보 노출", "cvss": 5.3, "found_at": "2026-11-05"},
        ],
        "mcp_detections": [],
    },
    # 9) FTP(21) 평문 포트 개방 - 포트 규정 위반
    {
        "hostname": "mail-prd-09", "env": "prd", "os": "CentOS 7",
        "owner_team": "그룹웨어팀", "owner_contact": "윤채원 / 010-5656-7878 / chaewon.yoon@example.com",
        "allowed_ports": [22, 25, 993], "open_ports": [21, 22, 25, 993],
        "vulnerabilities": [],
        "mcp_detections": [],
    },
    # 10) 정상 운영 서버
    {
        "hostname": "log-prd-10", "env": "prd", "os": "Rocky Linux 9",
        "owner_team": "보안관제센터", "owner_contact": "강태호 / 010-6767-8989 / taeho.kang@example.com",
        "allowed_ports": [22, 514, 9200], "open_ports": [22, 514, 9200],
        "vulnerabilities": [],
        "mcp_detections": [],
    },
    # 11) 개발자 PC형 서버의 stdio 비인가 MCP (포트 없음 · 비밀번호 노출)
    {
        "hostname": "dev-ai-11", "env": "dev", "os": "Ubuntu 24.04",
        "owner_team": "챗봇개발팀", "owner_contact": "서지민 / 010-7878-9090 / jimin.seo@example.com",
        "allowed_ports": [22], "open_ports": [22],
        "vulnerabilities": [],
        "mcp_detections": [
            {
                "port": None, "transport": "stdio", "process": "npx @community/mcp-shell (Claude Desktop 하위 프로세스)", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-17 09:12", "message": "stdio MCP 프로세스가 .env 파일 읽기 (DB_PASSWORD=Chat#2026! 포함)"},
                    {"source": "Nexus", "time": "2026-11-17 09:05", "message": "외부 npm 패키지 @community/mcp-shell 다운로드"},
                ],
            },
        ],
    },
    # 12) 긴급 취약점(CVSS 9.8) 패치 기한 초과
    {
        "hostname": "erp-prd-12", "env": "prd", "os": "Windows Server 2019",
        "owner_team": "ERP운영팀", "owner_contact": "임도현 / 010-8989-0101 / dohyun.lim@example.com",
        "allowed_ports": [443, 3389], "open_ports": [443, 3389],
        "vulnerabilities": [
            {"id": "CVE-2026-6006", "name": "Windows RDP 원격 코드 실행", "cvss": 9.8, "found_at": "2026-10-01"},
            {"id": "CVE-2026-6007", "name": "IIS 권한 상승", "cvss": 7.8, "found_at": "2026-10-15"},
        ],
        "mcp_detections": [],
    },
    # 13) 승인된 MCP(8800) 옆에 승인 안 된 복제 MCP(8801)
    {
        "hostname": "cicd-stg-13", "env": "stg", "os": "Ubuntu 22.04",
        "owner_team": "DevOps팀", "owner_contact": "배준서 / 010-9090-1212 / junseo.bae@example.com",
        "allowed_ports": [22, 8800], "open_ports": [22, 8800, 8801],
        "vulnerabilities": [],
        "mcp_detections": [
            {
                "port": 8800, "transport": "SSE", "process": "python deploy_mcp.py",
                "approved": True, "change_id": "CHG-2026-0915", "logs": [],
            },
            {
                "port": 8801, "transport": "SSE", "process": "python deploy_mcp.py --port 8801 (테스트용 복제 실행)", "approved": False,
                "logs": [
                    {"source": "EDR", "time": "2026-11-14 15:30", "message": "승인된 MCP와 동일한 실행 파일이 미등록 포트 8801로 추가 기동"},
                ],
            },
        ],
    },
    # 14) 외부 패키지로 설치된 비인가 MCP (외부 통신은 아직 없음)
    {
        "hostname": "vdi-dev-14", "env": "dev", "os": "Ubuntu 22.04",
        "owner_team": "데이터분석팀", "owner_contact": "조은서 / 010-0101-2323 / eunseo.jo@example.com",
        "allowed_ports": [22, 3389], "open_ports": [22, 3389, 7000],
        "vulnerabilities": [],
        "mcp_detections": [
            {
                "port": 7000, "transport": "SSE", "process": "node mcp-excel-reader", "approved": False,
                "logs": [
                    {"source": "Nexus", "time": "2026-11-10 11:00", "message": "외부 npm 패키지 mcp-excel-reader 다운로드"},
                    {"source": "EDR", "time": "2026-11-10 11:03", "message": "node 프로세스가 포트 7000 리슨 (외부 통신 없음)"},
                ],
            },
        ],
    },
    # 15) 정상 스테이징 API 서버
    {
        "hostname": "api-stg-15", "env": "stg", "os": "Rocky Linux 9",
        "owner_team": "결제개발팀", "owner_contact": "박서연 / 010-3333-4444 / seoyeon.park@example.com",
        "allowed_ports": [22, 443], "open_ports": [22, 443],
        "vulnerabilities": [],
        "mcp_detections": [],
    },
]


# ------------------------------------------------------------
# 서버별 감시 범위: EDR 이 설치되지 않은 서버 (나머지 서버는 EDR 설치됨)
# EDR 이 없으면 포트를 쓰지 않는 stdio MCP 를 볼 수단이 없으므로 '담당자 확인 필요 서버'가 됩니다
# ------------------------------------------------------------
EDR_NOT_INSTALLED = {
    "ml-gpu-06": "GPU 학습 성능 저하 우려로 EDR 설치 예외 승인 (보안예외 SEC-EX-2026-031)",
    "mail-prd-09": "CentOS 7 지원 종료로 EDR 에이전트 미지원",
    "erp-prd-12": "ERP 벤더 유지보수 계약상 EDR 설치 보류",
}


def add_edr_coverage(servers: list) -> None:
    """서버마다 edr_installed(설치 여부)와 edr_note(미설치 사유)를 붙입니다."""
    for s in servers:
        if s["hostname"] in EDR_NOT_INSTALLED:
            s["edr_installed"] = False
            s["edr_note"] = EDR_NOT_INSTALLED[s["hostname"]]
        else:
            s["edr_installed"] = True
            s["edr_note"] = ""


def write_json(filename: str, data: dict) -> str:
    """한글이 깨지지 않게 UTF-8과 ensure_ascii=False로 씁니다."""
    path = os.path.join(BASE, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


if __name__ == "__main__":
    servers = FIXED_SERVERS + EXTRA_SERVERS
    add_edr_coverage(servers)
    data = {
        "_comment": "교육용 가상 데이터입니다. 실제 사내 서버·토큰·연락처가 아닙니다.",
        "change_approvals": CHANGE_APPROVALS,
        "servers": servers,
    }
    write_json("servers.json", data)

    unauthorized = []
    for s in servers:
        for m in s["mcp_detections"]:
            if not m["approved"]:
                unauthorized.append(s["hostname"])
    print(f"생성: servers.json (서버 {len(servers)}대, 변경관리 승인 {len(CHANGE_APPROVALS)}건)")
    print(f"확인: 비인가 MCP 탐지 {len(unauthorized)}건 → {unauthorized}")

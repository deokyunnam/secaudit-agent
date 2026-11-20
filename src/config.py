# config.py - 프로젝트 전체에서 같이 쓰는 경로·모델 설정
from pathlib import Path

# 이 파일(src/config.py)의 부모의 부모 = minipjt 폴더
# 어느 폴더에서 실행해도 경로가 깨지지 않도록 절대 경로로 계산합니다
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
ISMS_DIR = DATA_DIR / "isms_p"                     # ISMS-P 인증기준 원문 (항목별 80개)
KISA_DIR = DATA_DIR / "kisa_guide"                 # 주요정보통신기반시설 취약점 분석·평가 상세가이드 (항목별 220개)
POLICY_DIR = DATA_DIR / "policies"                 # 사내 점검기준 (가상)
CHECK_ITEMS_FILE = DATA_DIR / "mcp_check_items.json"   # MCP 점검항목 매핑표
SERVERS_FILE = DATA_DIR / "servers.json"           # CMDB + 로그 + 변경관리 이력 (가상)
EXTERNAL_DIR = DATA_DIR / "external"               # 외부 참고자료 (MCP 공식 보안 권고, OWASP MCP Top 10, CVE) - 판정 근거 아님
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "secaudit_criteria"              # 판정 근거: ISMS-P + 사내기준
REFERENCE_COLLECTION_NAME = "secaudit_reference"   # 참고자료: 외부 자료 (판정 근거와 섞이지 않게 따로 저장)

REGION = "us-east-1"
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
CHAT_MODEL = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"   # 메인 에이전트 (11/19 us. 경로 4.5·4.6 일일 한도 초과 → global 교차 리전 경로 Sonnet 4.5 · 1·2차는 4.5, 3·4차 CSV 는 4.6 기준)
CHECK_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"   # 업무 범위 판별 (빠르고 저렴)

# 세션당 최대 도구 호출 횟수 (SERVICE.md 가드레일 5번)
MAX_TOOL_CALLS = 10

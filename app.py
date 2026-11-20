# app.py - 제출용 진입점 (POST /query)
"""
강사님 README 규약: miniprj/app.py 에 POST /query 진입점을 둔다.
실제 API 코드는 src/api.py 에 있고, 이 파일은 그것을 불러와 그대로 내보냅니다.

실행 (이 파일이 있는 폴더에서):
    uvicorn app:app --port 8000
    → http://localhost:8000/docs 에서 /query, /approve 테스트

호출 예시:
    curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\": \"api-prd-02 점검해줘\"}"

응답: {"answer": "...", "contexts": [...], "trace": [...], "thread_id": "...", "pending_approval": null}
"""
import sys
from pathlib import Path

# src 폴더 안의 모듈(api, agent, tools ...)을 import 할 수 있도록 경로에 추가합니다
SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from api import app  # noqa: E402  (경로를 추가한 뒤에 import 해야 합니다)


if __name__ == "__main__":
    # python app.py 로도 실행할 수 있게 합니다
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# api.py - 표준 API 규약 (POST /query) + HITL 승인용 POST /approve + 시연용 챗봇 화면 (GET /)
"""
실행 (저장소 루트에서 · 제출 규약 진입점 app.py 가 이 app 을 그대로 내보냄):
    uvicorn app:app --port 8000
    → http://localhost:8000 챗봇 화면 · http://localhost:8000/docs API 테스트

테스트:
    curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\": \"api-prd-02 점검해줘\"}"
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import run_query, resume_query

app = FastAPI(title="SecAudit-Agent")

CHAT_PAGE = Path(__file__).resolve().parent / "static" / "chat.html"


@app.get("/", include_in_schema=False)
def chat_page() -> FileResponse:
    """시연용 챗봇 화면 (브라우저에서 http://localhost:8000 접속). /query·/approve 를 그대로 호출합니다."""
    return FileResponse(CHAT_PAGE)


class QueryRequest(BaseModel):
    question: str
    thread_id: str | None = None   # 같은 대화를 이어가려면 이전 응답의 thread_id 를 넣습니다


class ApproveRequest(BaseModel):
    thread_id: str
    decision: str                  # approve / modify / reject
    args: dict | None = None       # modify 일 때 바꿀 값 (예: {"port": 9001})
    reason: str | None = None      # reject 일 때 사유


@app.post("/query")
def query(req: QueryRequest) -> dict:
    """응답: {answer, contexts, trace, thread_id, pending_approval}"""
    return run_query(req.question, req.thread_id)


@app.post("/approve")
def approve(req: ApproveRequest) -> dict:
    decision = {"decision": req.decision}
    if req.args:
        decision["args"] = req.args
    if req.reason:
        decision["reason"] = req.reason
    return resume_query(req.thread_id, decision)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

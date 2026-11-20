#!/bin/bash
# run.sh - 벡터 DB 생성 후 API 서버 실행 (minipjt 폴더에서 실행)
set -e

if [ ! -d "chroma_db" ]; then
  echo "[1/2] 벡터 DB 생성"
  python src/retriever.py
fi

echo "[2/2] API 서버 실행 → http://localhost:8000/docs"
uvicorn app:app --host 0.0.0.0 --port 8000

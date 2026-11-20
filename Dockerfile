# Dockerfile - 클린 환경 재현용 (선택사항)
# 빌드: docker build -t secaudit-agent .
# 실행: docker run --env-file .env -p 8000:8000 secaudit-agent
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/ data/
COPY app.py run.sh ./

EXPOSE 8000
CMD ["bash", "run.sh"]

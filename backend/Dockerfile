# ProGear FastAPI backend - used by docker-compose for local development.
# Build context is the backend/ directory:
#   docker build -t progear-backend ./backend
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-8000}"]

FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn

# Copy application code
COPY src/inference/app.py /app/app.py

# Environment and health
ENV MODEL_URI=models:/fraud-model/Production \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2", "--timeout", "30"]

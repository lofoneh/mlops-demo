FROM python:3.11-slim
WORKDIR /app
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
ENV MODEL_URI=models:/fraud-model/Production
EXPOSE 8000
CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "1"]

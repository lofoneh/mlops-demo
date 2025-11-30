from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
import os
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import pandas as pd
import logging

MODEL_URI = os.environ.get("MODEL_URI", "models:/fraud-model/Production")

app = FastAPI(title="Fraud Model API")
logging.info("Loading model from %s", MODEL_URI)
model = mlflow.pyfunc.load_model(MODEL_URI)

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["endpoint"])

class Transaction(BaseModel):
    amount: float
    feature_1: float
    feature_2: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(tx: Transaction):
    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    import time
    start = time.time()
    try:
        input_df = pd.DataFrame([tx.dict()])
        # Ensure numeric columns only
        input_df = input_df.select_dtypes(include=['number']).fillna(0)
        pred = model.predict_proba(input_df)[:,1] if hasattr(model, "predict_proba") else model.predict(input_df)
        latency = time.time() - start
        REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)
        return {"fraud_probability": float(pred[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

import logging
import os
from time import time

import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from fastapi.responses import Response

# MODEL_URI can be a model registry URI (models:/name/Stage) or runs:/<run_id>/model or local path
MODEL_URI = os.environ.get("MODEL_URI", "models:/fraud-model/Production")

app = FastAPI(title="Fraud Model API")
logging.info("Attempting to load model from %s", MODEL_URI)

# Try loading the model; if it fails, set `model` to None and capture the error.
model = None
_load_error = None


def _try_load(uri: str):
    """Attempt to load a model URI and return (model, error_str).
    Does not raise; returns (None, error_message) on failure."""
    try:
        m = mlflow.pyfunc.load_model(uri)
        logging.info("Model loaded successfully from %s", uri)
        return m, None
    except Exception as exc:
        return None, str(exc)


# 1) Try configured MODEL_URI directly
model, _load_error = _try_load(MODEL_URI)

# 2) If that failed and the URI is a registry-style URI, try resolving registered model versions
if model is None and MODEL_URI and MODEL_URI.startswith("models:/"):
    try:
        # Extract model name (models:/<name>/<stage_or_version>)
        remainder = MODEL_URI.split("models:/", 1)[1]
        model_name = remainder.split("/", 1)[0]
        logging.info("Attempting to resolve registered model '%s' via MLflow Registry", model_name)
        from mlflow.tracking import MlflowClient

        client = MlflowClient()
        try:
            # get_latest_versions returns a list of ModelVersion objects
            versions = client.get_latest_versions(model_name)
        except Exception:
            versions = []

        # Try each returned version (ordered as provided) using models:/name/<version>
        for v in versions:
            try_uri = f"models:/{model_name}/{v.version}"
            model, _load_error = _try_load(try_uri)
            if model:
                break
    except Exception:
        logging.exception("Error while attempting to resolve registered model for %s", MODEL_URI)

# 3) Fallback: scan recent runs across experiments for an artifact path named 'model'
if model is None:
    logging.info("Falling back to scanning recent runs for a 'model' artifact")
    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient()
        # use mlflow.search_experiments for broader compatibility
        experiments = mlflow.search_experiments()
        # iterate experiments in recent order by creation time
        # For each experiment, search for recent runs and check for a 'model' artifact
        for exp in sorted(experiments, key=lambda e: getattr(e, 'creation_time', 0), reverse=True):
            try:
                runs = client.search_runs([exp.experiment_id], order_by=["attributes.start_time DESC"], max_results=50)
            except Exception:
                continue
            for r in runs:
                try:
                    artifacts = client.list_artifacts(r.info.run_id, path="model")
                    if artifacts:
                        candidate = f"runs:/{r.info.run_id}/model"
                        model, _load_error = _try_load(candidate)
                        if model:
                            logging.info("Resolved model from run %s", r.info.run_id)
                            break
                except Exception:
                    # ignore runs we can't inspect
                    continue
            if model:
                break
    except Exception:
        logging.exception("Error while scanning runs to find model artifact")

if model is None:
    logging.warning("Model not loaded at startup. Last error: %s", _load_error)

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Request latency", ["endpoint"])


class Transaction(BaseModel):
    amount: float
    feature_1: float
    feature_2: float


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None, "model_error": _load_error}


@app.post("/predict")
def predict(tx: Transaction):
    """Predict fraud probability for a transaction."""
    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    start = time()

    # Guard: if the model failed to load, return 503 with guidance
    if model is None:
        detail = (
            "Model not loaded. Startup error: "
            + (_load_error or "unknown")
            + ". Set MODEL_URI to a valid path (e.g. 'runs:/<run_id>/model') or register the model "
            + "in MLflow Model Registry."
        )
        raise HTTPException(status_code=503, detail=detail)

    try:
        input_df = pd.DataFrame([tx.dict()])
        # Ensure numeric columns only
        input_df = input_df.select_dtypes(include=['number']).fillna(0)
        
        # Prefer predict_proba when available on the underlying model; use callable check to satisfy static analyzers
        predict_proba_fn = getattr(model, "predict_proba", None)
        if callable(predict_proba_fn):
            proba_result = np.asarray(predict_proba_fn(input_df))
            # Extract class 1 probability (fraud) from 2D result
            if proba_result.ndim == 2 and proba_result.shape[1] > 1:
                pred = proba_result[:, 1]
            else:
                pred = proba_result
        else:
            # Fall back to model.predict which may return probabilities or labels
            pred_result = model.predict(input_df)
            proba_result = np.asarray(pred_result)
            if proba_result.ndim == 2 and proba_result.shape[1] > 1:
                pred = proba_result[:, 1]
            else:
                pred = proba_result
        
        latency = time() - start
        REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)
        return {"fraud_probability": float(pred[0])}
    except Exception as e:
        logging.exception("Prediction error")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

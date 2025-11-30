# Full step-by-step: setup platform + run project (kind)

## Prerequisites
- Docker (desktop or engine) — ensure it's running.
- kind (`brew install kind` or https://kind.sigs.k8s.io/)
- kubectl (matching k8s version)
- Python 3.13
- git

## Ideal kind profile for MLOps practice
For local experiments (small models like RandomForest), the following kind node profile works well:

- 1 control-plane node
- 2 worker nodes
- CPU: each node inherits Docker host CPU; give Docker ~4+ CPUs
- Memory: Docker host 8+ GB (prefer 12+ GB if possible)
- Storage: ephemeral is fine; use hostPath or local PV for volumes if needed.

This kind config file is included at `scripts/kind-config.yaml`.

## Step-by-step

### 1) Start MLflow tracking server (local)
```
cd mlflow
docker compose up -d
# MLflow UI at http://localhost:5000
```

### 2) Create kind cluster
```
bash scripts/create_kind_cluster.sh
# verifies cluster with: kubectl get nodes
```

### 3) Build the inference Docker image (local)
```
bash scripts/build_and_load_kind.sh
# This builds src/inference image and loads it into kind (no remote registry needed)
```

### 4) Deploy k8s manifests
```
bash scripts/deploy_to_kind.sh
# This applies infra/*.yaml to the kind cluster
```

### 5) Test the service
Port-forward to access API locally:
```
kubectl -n mlops port-forward svc/fraud-model-svc 8000:80
curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"amount":100, "feature_1":0.1, "feature_2":1.2}' | jq .
```

### 6) Load a trained model into MLflow (local training)
```
python src/train.py --data-path data/transactions.csv --mlflow-uri http://localhost:5000 --experiment-name local_exp
# Note the run ID printed or check MLflow UI, then update environment variable MODEL_URI if testing inference via runs:/...
```

### 7) Prometheus (optional)
See `infra/README_KIND.md` for instructions to deploy a lightweight Prometheus and Grafana stack in the kind cluster and scrape `/metrics`.


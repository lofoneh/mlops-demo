# MLOps Fraud Demo — KIND (local) Edition

This repository contains a complete end-to-end MLOps practice project tailored for **kind** (Kubernetes in Docker).
It includes training scripts (MLflow), a FastAPI inference server, Dockerfiles, Kubernetes manifests (for kind),
and helper scripts to build, load images to kind, and deploy locally.

## What’s included
- `src/` : training and inference code
- `mlflow/` : docker-compose to run MLflow locally
- `infra/` : k8s manifests suitable for kind
- `scripts/` : helper scripts (build image, load to kind, deploy)
- `.github/workflows/ci-cd.yml` : example CI/CD (keeps placeholders)

## Quick local setup (summary)
1. Install Docker, kind, kubectl, and Python 3.11.
2. Start MLflow: `docker compose -f mlflow/docker-compose.yml up -d`
3. Create kind cluster: `scripts/create_kind_cluster.sh`
4. Build and load image to kind: `scripts/build_and_load_kind.sh`
5. Deploy to kind: `scripts/deploy_to_kind.sh`
6. Port-forward service or use `kubectl port-forward svc/fraud-model-svc 8000:80` to access API.
7. Check MLflow UI: http://localhost:5000
8. Prometheus & Grafana instructions are in `infra/README_KIND.md`.

See the full Step-by-step setup in `SETUP_KIND.md`.


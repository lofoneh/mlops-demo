#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${NAMESPACE:-mlops}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
  echo "ERROR: kubectl is not installed."
  exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
  echo "ERROR: Kubernetes cluster not accessible."
  exit 1
fi

echo "📝 Applying namespace..."
kubectl apply -f infra/namespace.yaml

echo "🚀 Deploying fraud-model service..."
kubectl apply -f infra/k8s-deployment.yaml
kubectl apply -f infra/k8s-service.yaml

echo "✓ Deployment status:"
kubectl -n "${NAMESPACE}" get all

echo ""
echo "✓ Deployment complete!"
echo "  Port-forward: kubectl -n ${NAMESPACE} port-forward svc/fraud-model-svc 8000:80"
echo "  Logs: kubectl -n ${NAMESPACE} logs -f deployment/fraud-model"
echo "  Health: curl http://localhost:8000/health"

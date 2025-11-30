#!/usr/bin/env bash
set -e
NAMESPACE=${NAMESPACE:-mlops}
echo "Applying namespace..."
kubectl apply -f infra/namespace.yaml
echo "Deploying app..."
kubectl apply -f infra/k8s-deployment.yaml
kubectl apply -f infra/k8s-service.yaml
kubectl -n ${NAMESPACE} get all
echo "Deployed. Use 'kubectl -n ${NAMESPACE} port-forward svc/fraud-model-svc 8000:80' to access API."

#!/usr/bin/env bash
set -euo pipefail

KIND_CLUSTER_NAME=${KIND_CLUSTER_NAME:-mlops-kind}

# Check if kind is installed
if ! command -v kind &> /dev/null; then
  echo "ERROR: kind is not installed. Please install kind: https://kind.sigs.k8s.io/docs/user/quick-start/"
  exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
  echo "ERROR: kubectl is not installed. Please install kubectl."
  exit 1
fi

# Check if cluster already exists
if kind get clusters | grep -q "^${KIND_CLUSTER_NAME}$"; then
  echo "ℹ Cluster '${KIND_CLUSTER_NAME}' already exists. Skipping creation."
  exit 0
fi

echo "📦 Creating kind cluster '${KIND_CLUSTER_NAME}'..."
kind create cluster --name "${KIND_CLUSTER_NAME}" --config scripts/kind-config.yaml || {
  echo "ERROR: Failed to create cluster."
  exit 1
}

echo "✓ Cluster info:"
kubectl cluster-info
echo "✓ Nodes:"
kubectl get nodes

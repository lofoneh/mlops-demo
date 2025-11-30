#!/usr/bin/env bash
set -e
KIND_CLUSTER_NAME=${KIND_CLUSTER_NAME:-mlops-kind}
echo "Creating kind cluster '${KIND_CLUSTER_NAME}'..."
kind create cluster --name "${KIND_CLUSTER_NAME}" --config scripts/kind-config.yaml
kubectl cluster-info
kubectl get nodes

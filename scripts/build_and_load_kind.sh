#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-fraud-model:latest}
KIND_CLUSTER_NAME=${KIND_CLUSTER_NAME:-mlops-kind}

# Check if Docker is running
if ! docker ps &> /dev/null; then
  echo "ERROR: Docker is not running. Please start Docker."
  exit 1
fi

# Check if kind cluster exists
if ! kind get clusters | grep -q "^${KIND_CLUSTER_NAME}$"; then
  echo "ERROR: Kind cluster '${KIND_CLUSTER_NAME}' not found. Run create_kind_cluster.sh first."
  exit 1
fi

echo "🔨 Building Docker image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" -f src/inference/Dockerfile . || {
  echo "ERROR: Docker build failed."
  exit 1
}

echo "📤 Loading image into kind cluster '${KIND_CLUSTER_NAME}'..."
kind load docker-image "${IMAGE_NAME}" --name "${KIND_CLUSTER_NAME}" || {
  echo "ERROR: Failed to load image into kind."
  exit 1
}

echo "✓ Image loaded successfully."

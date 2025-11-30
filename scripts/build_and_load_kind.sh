#!/usr/bin/env bash
set -e
# Builds the local inference image and loads it into kind cluster
IMAGE_NAME=${IMAGE_NAME:-fraud-model:latest}
echo "Building Docker image ${IMAGE_NAME} (context: src/inference)..."
docker build -t ${IMAGE_NAME} -f src/inference/Dockerfile src/inference
echo "Loading image into kind..."
kind load docker-image ${IMAGE_NAME} --name ${KIND_CLUSTER_NAME:-mlops-kind}
echo "Image loaded."

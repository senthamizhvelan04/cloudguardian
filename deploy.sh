#!/bin/bash
set -e

REGION="ap-south-1"
IMAGE="788607671185.dkr.ecr.ap-south-1.amazonaws.com/cloudguardian:latest"
CONTAINER="cloudguardian"

aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin \
  788607671185.dkr.ecr.ap-south-1.amazonaws.com

docker pull "$IMAGE"

docker rm -f "$CONTAINER" 2>/dev/null || true

docker run -d \
  --restart unless-stopped \
  --name "$CONTAINER" \
  --env-file /etc/cloudguardian/cloudguardian.env \
  -p 80:8000 \
  "$IMAGE"

docker ps

#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/ready
curl -fsS http://localhost:8000/api/v1/incidents

#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 "$(nproc)"); do yes > /dev/null & done
sleep "${1:-120}"
pkill yes || true

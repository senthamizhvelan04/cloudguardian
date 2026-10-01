#!/usr/bin/env bash
set -euo pipefail
if docker ps --format '{{.Names}}' | grep -q cloudguardian; then
    sudo docker stop cloudguardian
else
    sudo systemctl stop cloudguardian-test.service
fi

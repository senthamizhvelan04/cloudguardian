#!/usr/bin/env bash
set -euo pipefail
FILE=/tmp/cloudguardian-disk-test
HOLD_SECONDS=${2:-180}
dd if=/dev/zero of="$FILE" bs=10M count="${1:-50}" status=progress
sleep "$HOLD_SECONDS"
rm -f "$FILE"

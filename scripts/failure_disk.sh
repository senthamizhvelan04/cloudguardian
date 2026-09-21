#!/usr/bin/env bash
set -euo pipefail
FILE=/tmp/cloudguardian-disk-test
dd if=/dev/zero of="$FILE" bs=10M count="${1:-50}" status=progress
rm -f "$FILE"

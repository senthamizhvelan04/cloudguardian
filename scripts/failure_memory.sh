#!/usr/bin/env bash
set -euo pipefail
LIMIT_MB=${1:-500}
HOLD_SECONDS=${2:-180}
python3 - "$LIMIT_MB" "$HOLD_SECONDS" <<'PY'
import time
import sys
limit = int(sys.argv[1])
hold = int(sys.argv[2])
x = []
try:
    for i in range(limit // 10):
        x.append(bytearray(10 * 1024 * 1024))
        time.sleep(0.5)
    time.sleep(hold)
except KeyboardInterrupt:
    pass
PY

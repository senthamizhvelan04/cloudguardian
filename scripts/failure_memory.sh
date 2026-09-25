#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import time
x=[]
try:
    while True:
        x.append(bytearray(10*1024*1024))
        time.sleep(1)
except KeyboardInterrupt:
    pass
PY

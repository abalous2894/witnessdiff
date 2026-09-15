#!/usr/bin/env bash
# Supply-chain gate: fail when viewer production tree has high/critical npm audit findings.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VIEWER="${ROOT}/apps/viewer"

if [[ ! -f "${VIEWER}/package-lock.json" ]]; then
  echo "[npm-audit-gate] missing apps/viewer/package-lock.json"
  exit 1
fi

cd "${VIEWER}"

payload="$(npm audit --omit=dev --json 2>/dev/null || true)"
counts="$(PAYLOAD="${payload}" python3 - <<'PY'
import json
import os
import sys

raw = os.environ.get("PAYLOAD", "").strip()
if not raw:
    print("high=0 critical=0 parse_error=1")
    sys.exit(0)
start = raw.find("{")
if start < 0:
    print("high=0 critical=0 parse_error=1")
    sys.exit(0)
try:
    data = json.loads(raw[start:])
except json.JSONDecodeError:
    print("high=0 critical=0 parse_error=1")
    sys.exit(0)
v = data.get("metadata", {}).get("vulnerabilities", {})
print(f"high={int(v.get('high', 0))} critical={int(v.get('critical', 0))} parse_error=0")
PY
)"

eval "${counts}"
if [[ "${parse_error}" == "1" ]]; then
  echo "[npm-audit-gate] could not parse npm audit JSON"
  exit 1
fi

if [[ "${high}" -gt 0 || "${critical}" -gt 0 ]]; then
  echo "[npm-audit-gate] FAIL viewer production audit high=${high} critical=${critical}"
  exit 1
fi

echo "[npm-audit-gate] OK viewer: 0 high/critical production vulnerabilities"

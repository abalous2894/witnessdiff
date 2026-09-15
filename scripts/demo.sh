#!/usr/bin/env bash
# WitnessDiff 90-second demo script — run from repo root with API on :8080
set -euo pipefail

API="${WITNESSDIFF_API:-http://localhost:8080}"

echo "== WitnessDiff demo =="
echo "API: $API"
echo

echo "1) Health check"
curl -sf "$API/health" | python3 -m json.tool
echo

echo "2) Silent omission (COMPLETENESS_OVERCLAIM)"
curl -sf -X POST "$API/v1/demo/silent-omission" | python3 -m json.tool
echo

echo "3) CLI compare (same fixture)"
witnessdiff compare \
  fixtures/evidence/silent-omission.reference.json \
  fixtures/evidence/silent-omission.evidence.json || true
echo

echo "4) Evidence suite (15 cases)"
witnessdiff run-evidence-suite
echo

echo "5) Behavioral suite (10 cases)"
witnessdiff run-behavioral-suite
echo

echo "Done. Open viewer at http://localhost:5173 (docker compose) or npm run dev in apps/viewer."

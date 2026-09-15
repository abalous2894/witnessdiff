#!/usr/bin/env bash
# Supply-chain gate: fail on known vulnerabilities in production dependency tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if ! command -v pip-audit >/dev/null 2>&1; then
  echo "[pip-audit-gate] pip-audit not installed (pip install pip-audit)"
  exit 1
fi

echo "[pip-audit-gate] auditing production dependencies (skip editable witnessdiff)"
pip-audit . --skip-editable
echo "[pip-audit-gate] OK — no known production vulnerabilities"

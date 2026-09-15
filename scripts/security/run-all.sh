#!/usr/bin/env bash
# WitnessDiff unified security + regression gate (Aevesa-style shift-left sweep).
#
# Local escape hatches:
#   WITNESSDIFF_SKIP_SECURITY=1     skip entire gate
#   WITNESSDIFF_SKIP_GITLEAKS=1     skip secret scan
#   WITNESSDIFF_SKIP_SEMGREP=1      skip semgrep SAST
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${ROOT}"

if [[ "${WITNESSDIFF_SKIP_SECURITY:-}" == "1" ]]; then
  echo "[security] WITNESSDIFF_SKIP_SECURITY=1 — skipped"
  exit 0
fi

if [[ -d "${ROOT}/.venv" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT}/.venv/bin/activate"
fi

run_step() {
  local label="$1"
  shift
  echo ""
  echo "▶ ${label}"
  "$@"
  echo "✓ ${label}"
}

run_step "ruff lint" ruff check src tests
run_step "bandit SAST (src/)" bandit -r src -ll -q
run_step "pip-audit production tree" bash "${ROOT}/scripts/security/pip-audit-gate.sh"
run_step "npm audit (viewer production)" bash "${ROOT}/scripts/security/npm-audit-gate.sh"
run_step "pytest (unit + red team + API security)" pytest -q
run_step "witness integrity + behavioral baselines" witnessdiff run-all-suites

if [[ "${WITNESSDIFF_SKIP_SEMGREP:-}" != "1" ]] && command -v semgrep >/dev/null 2>&1; then
  run_step "semgrep (python + fastapi)" semgrep scan \
    --config p/python \
    --config p/fastapi \
    --config p/owasp-top-ten \
    --error \
    --metrics=off \
    src/
elif [[ "${WITNESSDIFF_SKIP_SEMGREP:-}" != "1" ]]; then
  echo ""
  echo "▶ semgrep — not installed locally (CI runs this step)"
fi

if [[ "${WITNESSDIFF_SKIP_GITLEAKS:-}" != "1" ]]; then
  GITLEAKS_BIN="${GITLEAKS_BIN:-}"
  if [[ -z "${GITLEAKS_BIN}" ]] && command -v gitleaks >/dev/null 2>&1; then
    GITLEAKS_BIN="gitleaks"
  fi
  if [[ -n "${GITLEAKS_BIN}" ]]; then
    run_step "gitleaks delta scan" env GITLEAKS_BIN="${GITLEAKS_BIN}" bash "${ROOT}/scripts/security/ci-gitleaks-gate.sh"
  else
    echo ""
    echo "▶ gitleaks — not installed locally (CI runs delta scan)"
  fi
fi

echo ""
echo "[security] All WitnessDiff gates passed"

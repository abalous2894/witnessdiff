#!/usr/bin/env bash
# CI gitleaks — scan push/PR delta only (matches Aevesa pre-push semantics).
#
# Env: GITHUB_EVENT_NAME, GITHUB_SHA, GITHUB_EVENT_BEFORE, GITHUB_EVENT_PATH
# Override: WITNESSDIFF_CI_GITLEAKS_LOG_OPTS=base..head
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GITLEAKS_BIN="${GITLEAKS_BIN:-gitleaks}"
if [[ -x "${GITLEAKS_BIN}" ]]; then
  :
elif command -v gitleaks >/dev/null 2>&1; then
  GITLEAKS_BIN="$(command -v gitleaks)"
else
  echo "[ci-gitleaks] gitleaks binary not found (set GITLEAKS_BIN or install via ci-gitleaks-install.sh)"
  exit 1
fi

resolve_log_opts() {
  if [[ -n "${WITNESSDIFF_CI_GITLEAKS_LOG_OPTS:-}" ]]; then
    echo "${WITNESSDIFF_CI_GITLEAKS_LOG_OPTS}"
    return
  fi

  local event="${GITHUB_EVENT_NAME:-}"
  local sha="${GITHUB_SHA:-HEAD}"

  if [[ "${event}" == "pull_request" && -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
    local base
    base="$(python3 - <<'PY'
import json, os, sys
path = os.environ.get("GITHUB_EVENT_PATH", "")
if not path:
    sys.exit(0)
with open(path, encoding="utf-8") as f:
    payload = json.load(f)
base = payload.get("pull_request", {}).get("base", {}).get("sha", "")
if base:
    print(base)
PY
)"
    if [[ -n "${base}" ]]; then
      echo "${base}..${sha}"
      return
    fi
  fi

  if [[ "${event}" == "push" ]]; then
    local before="${GITHUB_EVENT_BEFORE:-}"
    if [[ -n "${before}" && ! "${before}" =~ ^0+$ ]]; then
      echo "${before}..${sha}"
      return
    fi
  fi

  local parent
  if parent="$(git rev-parse "${sha}^" 2>/dev/null)"; then
    echo "${parent}..${sha}"
    return
  fi

  echo "${sha}~1..${sha}"
}

LOG_OPTS="$(resolve_log_opts)"
echo "[ci-gitleaks] delta scan: ${LOG_OPTS}"

args=(detect --source "${ROOT}" --redact --verbose --log-opts "${LOG_OPTS}")
if [[ -f "${ROOT}/.gitleaks.toml" ]]; then
  args+=(--config "${ROOT}/.gitleaks.toml")
fi

"${GITLEAKS_BIN}" "${args[@]}"
echo "[ci-gitleaks] OK — no secrets in delta"

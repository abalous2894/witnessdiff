#!/usr/bin/env bash
# Install pinned gitleaks binary for CI (stdout path on success).
set -euo pipefail

GITLEAKS_VERSION="${GITLEAKS_VERSION:-8.22.1}"
ARCHIVE="gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
SHA256="${GITLEAKS_SHA256:-2f92ab3b8e08319ac30836c32b90818e01519c3a4982771e4f45a7f5607872f7}"

INSTALL_DIR="$(pwd)"
curl -fsSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/${ARCHIVE}" -o "${ARCHIVE}"
echo "${SHA256}  ${ARCHIVE}" | sha256sum -c - >/dev/null
tar -xzf "${ARCHIVE}" gitleaks
chmod +x gitleaks
# stdout must be ONLY the binary path (CI captures this for GITLEAKS_BIN)
printf '%s\n' "${INSTALL_DIR}/gitleaks"

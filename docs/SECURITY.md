# Security

WitnessDiff applies Aevesa-style shift-left gates adapted for a public Python/FastAPI evaluation repo.

## Threat model

See [threat-model.md](threat-model.md). v1 scope is synthetic fixture regression — not securing live agent runtimes.

## CI gates (every PR and push to `main`)

Workflows:

- [`.github/workflows/security-sweep.yml`](../.github/workflows/security-sweep.yml) — shift-left gates below
- [`.github/workflows/codeql.yml`](../.github/workflows/codeql.yml) — GitHub CodeQL static analysis (Python + TypeScript viewer)

| Gate | Tool | Fails on |
|------|------|----------|
| Secret scan (delta) | gitleaks 8.22.1 | New secrets in push/PR delta |
| Lint | ruff | Style/import errors |
| Python SAST | bandit | Medium+ findings in `src/` |
| Python supply-chain | pip-audit | Known vulns in production deps |
| Viewer supply-chain | npm audit | High/critical in production tree |
| Cross-ecosystem SAST | semgrep | OWASP / Python / FastAPI rules |
| Deep static analysis | CodeQL | Python + JavaScript/TypeScript security queries |
| Unit + red team | pytest | INV-01–07 oracle falsifiers, API boundaries |
| Regression | witnessdiff CLI | Fixture or baseline drift |

Regression-only workflow [`.github/workflows/regression.yml`](../.github/workflows/regression.yml) still runs on all pushes/PRs.

## Red-team invariants (offline)

Implemented in `tests/test_red_team.py`:

| ID | Invariant |
|----|-----------|
| INV-01 | Silent omission under `complete_path` never yields `COMPLETE` |
| INV-02 | `session_id` mismatch → `INVALID_INPUT` |
| INV-03 | Reference superset + `complete_path` → `COMPLETENESS_OVERCLAIM` |
| INV-04 | Prohibited tools never `COMPLIANT` |
| INV-05 | Comparator is deterministic |
| INV-06 | Unsupported schemas rejected at parse boundary |
| INV-07 | `declared_count` overclaim + `complete_path` → `COMPLETENESS_OVERCLAIM` |

API boundary checks live in `tests/test_api_security.py`.

## Run locally (full sweep)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
chmod +x scripts/security/*.sh
./scripts/security/run-all.sh
```

Escape hatches (local only):

- `WITNESSDIFF_SKIP_SECURITY=1` — skip entire sweep
- `WITNESSDIFF_SKIP_GITLEAKS=1` — skip gitleaks
- `WITNESSDIFF_SKIP_SEMGREP=1` — skip semgrep

Install optional tools for parity with CI:

```bash
pip install semgrep
# gitleaks: bash scripts/security/ci-gitleaks-install.sh
```

## Reporting vulnerabilities

This is a public research/evaluation repo. Open a GitHub Security Advisory or issue on [github.com/abalous2894/witnessdiff](https://github.com/abalous2894/witnessdiff) with reproduction steps. Do not commit secrets or real customer traces to fixtures.

## Claim boundary (security relevance)

WitnessDiff does not authenticate MCP servers or prove runtime behavior. Treat reference traces as test oracles you supply; do not use export-clean verdicts as proof of production conduct without independent instrumentation.

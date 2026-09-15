# WitnessDiff

[![regression](https://github.com/abalous2894/witnessdiff/actions/workflows/regression.yml/badge.svg)](https://github.com/abalous2894/witnessdiff/actions/workflows/regression.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

**Regression testing for what AI-agent execution exports leave out.**

WitnessDiff compares an **instrumented reference trace** (what you trust was recorded during execution) with an **evidence bundle** (what an agent, platform, or exporter claims happened). It flags omissions, substitutions, reordering, and completeness overclaims **before** anyone treats a "clean export" as a complete session witness.

This project is **independent** of [Aevesa](https://aevesa.com). It applies adjacent expertise in agent evidence and witness completeness using neutral schemas and synthetic fixtures only.

> **Resume line:** Open-source Python/FastAPI evaluation system comparing instrumented MCP-agent traces with exported evidence bundles; deterministic behavioral + witness-integrity graders, React replay viewer, CI regression suite (25 scenarios). [github.com/abalous2894/witnessdiff](https://github.com/abalous2894/witnessdiff)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Compare a reference trace to an evidence bundle
witnessdiff compare \
  fixtures/evidence/silent-omission.reference.json \
  fixtures/evidence/silent-omission.evidence.json

# Run all evidence-integrity fixtures (15 cases)
witnessdiff run-evidence-suite

# Run behavioral policy fixtures (10 cases)
witnessdiff run-behavioral-suite

# Run both suites with baseline comparison (25 total)
witnessdiff run-all-suites

# Start API (in-memory store without DATABASE_URL)
witnessdiff serve

# Postgres + API + viewer via Docker
docker compose up --build
# Viewer → http://localhost:5173 · API → http://localhost:8080

# 90s demo script (API must be running)
chmod +x scripts/demo.sh && ./scripts/demo.sh

# Viewer dev (API must be running on :8080)
cd apps/viewer && npm install && npm run dev

# Run tests
pytest
```

## Demo

The headline scenario is **silent omission**: four tool hops ran, the export presents three, and still claims `complete_path`.

```bash
witnessdiff compare \
  fixtures/evidence/silent-omission.reference.json \
  fixtures/evidence/silent-omission.evidence.json
# → COMPLETENESS_OVERCLAIM

curl -X POST http://localhost:8080/v1/demo/silent-omission   # when API is up
```

Full walkthrough: [docs/DEMO.md](docs/DEMO.md) · Results matrix: [docs/RESULTS.md](docs/RESULTS.md) · Deploy: [docs/DEPLOY.md](docs/DEPLOY.md)

## Two evaluation lanes

| Lane | Question | Example failure |
|------|----------|-----------------|
| **Behavioral** | Did the agent choose a permitted tool with valid arguments? | Calls `refund_order` without required approval |
| **Witness integrity** | Does the export faithfully represent the instrumented path? | Four tool hops ran; bundle presents three while claiming completeness |

Behavioral scenarios live under `fixtures/behavioral/`. Witness-integrity pairs live under `fixtures/evidence/`.

## Claim boundary (read this first)

WitnessDiff does **not** prove "what actually happened" from arbitrary logs. It compares:

1. A **reference trace** you treat as ground truth for the test (instrumented sandbox, synthetic runner, or your own capture pipeline).
2. An **evidence bundle** that makes a declarative claim about tool hops and completeness.

If the reference trace is wrong or incomplete, WitnessDiff cannot fix that. It tests whether the bundle **supports the completeness claim it makes** relative to the reference you supplied.

## Public verdict labels

| WitnessDiff verdict | Meaning |
|---------------------|---------|
| `COMPLETE` | Evidence bundle matches reference hop set |
| `WITNESS_OMISSION` | Reference contains hops not attested in the bundle (silent omission) |
| `EXPORT_TRUNCATION` | Bundle contains hops not present in the reference |
| `MISMATCH` | Tool identity, ordering, or binding fields diverge |
| `COMPLETENESS_OVERCLAIM` | Bundle asserts a complete path but fails integrity checks |

## Behavioral verdict labels

| Verdict | Meaning |
|---------|---------|
| `COMPLIANT` | Tool choices and arguments satisfy deterministic policy |
| `POLICY_VIOLATION` | Sensitive tool used without approval |
| `PROHIBITED_TOOL` | Blocked tool invoked |
| `INVALID_TOOL_ARGS` | Missing or empty required arguments |

See [docs/methodology.md](docs/methodology.md) for grader design and oracle alignment notes.

## Repository layout

```text
witnessdiff/
  src/witnessdiff/     Core parsers, comparators, graders, CLI, API
  fixtures/            Versioned JSON scenarios (synthetic only)
  tests/               Pytest regression suite
  apps/viewer/         React replay viewer
  scripts/demo.sh      90-second demo script
  docs/                Methodology, threat model, demo, deploy, results
```

## GitHub topics (suggested)

`ai-agents` · `mcp` · `evaluation` · `regression-testing` · `evidence-integrity` · `fastapi` · `python`

## Development roadmap

- [x] Week 1: CLI, schemas, evidence comparators, first fixtures
- [x] Week 2: Behavioral graders, baseline regression, CI gate
- [x] Week 3: Full witness comparator matrix (10 evidence + 5 behavioral fixtures)
- [x] Week 4: FastAPI + Postgres + Docker Compose
- [x] Week 5: Minimal viewer + public demo deploy
- [x] Week 6: 25 scenarios, demo docs, hardened README (v1.0.0)

## License

Apache-2.0. See [LICENSE](LICENSE).

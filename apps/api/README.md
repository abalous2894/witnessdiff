# WitnessDiff API

FastAPI service for persisting witness-integrity comparison runs in PostgreSQL.

## Local (in-memory store)

```bash
pip install -e ".[dev]"
witnessdiff serve
# → http://127.0.0.1:8080/health
```

Without `DATABASE_URL`, runs persist in memory only (resets on restart).

## Docker Compose (Postgres + API)

```bash
docker compose up --build
# API → http://localhost:8080
# Postgres → localhost:5433
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health and store kind |
| POST | `/v1/compare` | Compare reference + evidence, persist run |
| GET | `/v1/runs` | List recent runs |
| GET | `/v1/runs/{id}` | Fetch run with full report |
| POST | `/v1/suites/{evidence\|behavioral}/run` | Execute fixture suite |

### Compare example

```bash
curl -s http://localhost:8080/v1/compare \
  -H 'Content-Type: application/json' \
  -d @- <<'EOF'
{
  "reference": { "...": "witnessdiff.reference-trace/v1" },
  "evidence": { "...": "witnessdiff.evidence-bundle/v1" }
}
EOF
```

Implementation lives in `src/witnessdiff/api/`.

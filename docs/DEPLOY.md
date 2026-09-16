# Deployment

WitnessDiff can run locally, via Docker Compose, or on Render using the included blueprint.

## Local development

```bash
pip install -e ".[dev]"
witnessdiff serve                    # API :8080, in-memory store
cd apps/viewer && npm install && npm run dev   # viewer :5173, proxies to API
```

Set `DATABASE_URL` to use Postgres instead of the in-memory store.

## Docker Compose (full stack)

```bash
docker compose up --build
```

| Service | Port | Notes |
|---------|------|-------|
| `api` | 8081 (override: `WITNESSDIFF_HOST_API_PORT`) | FastAPI + Postgres |
| `db` | internal only | Postgres 16 (no host bind; avoids port clashes) |
| `viewer` | 5173 | nginx serving built React app |

Fixtures are mounted read-only; suite endpoints use `WITNESSDIFF_FIXTURES_ROOT`.

## Render (public demo)

[`render.yaml`](../render.yaml) defines:

- **witnessdiff-api** — Docker web service, Postgres via `DATABASE_URL`
- **witnessdiff-viewer** — static viewer container; nginx proxies `/v1` to API host
- **witnessdiff-db** — free Postgres

### Steps

1. Fork or connect [github.com/abalous2894/witnessdiff](https://github.com/abalous2894/witnessdiff).
2. Create a **Blueprint** from `render.yaml` in the Render dashboard.
3. Set `WITNESSDIFF_CORS_ORIGINS` on the API to your viewer URL (blueprint defaults to `https://witnessdiff-viewer.onrender.com`).
4. After deploy, open the viewer URL and use **Load demo run**.

### Environment variables

| Variable | Service | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | API | Postgres connection (auto from Render DB) |
| `WITNESSDIFF_FIXTURES_ROOT` | API | Path to fixture directory (`/app/fixtures` in image) |
| `WITNESSDIFF_CORS_ORIGINS` | API | Comma-separated viewer origins |
| `WITNESSDIFF_API_HOST` | Viewer | Internal hostname for API reverse proxy |

## Health check

```bash
curl -s https://your-api.onrender.com/health
```

Expected: `{"ok": true, "store": "postgres"}` (or `"memory"` locally without DB).

# WitnessDiff Viewer

Minimal React UI for replaying witness-integrity comparison runs.

## Local development

Terminal A — API:

```bash
pip install -e ".[dev]"
witnessdiff serve
```

Terminal B — viewer (proxies `/v1` to the API):

```bash
cd apps/viewer
npm install
npm run dev
# → http://127.0.0.1:5173
```

Click **Load silent-omission demo** to persist a failing run and highlight the missing `policy_check` hop.

## Docker Compose (viewer + API + Postgres)

```bash
docker compose up --build
# Viewer → http://localhost:5173
# API    → http://localhost:8080
```

Nginx in the viewer container proxies `/v1` and `/health` to the API service.

## Static deploy (Render / Netlify / Fly)

Build with the public API URL:

```bash
cd apps/viewer
VITE_API_BASE_URL=https://your-api.example.com npm run build
```

Deploy the `dist/` folder as a static site. Enable CORS on the API via `WITNESSDIFF_CORS_ORIGINS`.

See [render.yaml](../../render.yaml) for an optional split-service blueprint.

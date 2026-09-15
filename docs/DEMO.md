# Demo guide

WitnessDiff ships a **90-second walkthrough** covering the headline failure mode: a platform export that looks clean but omits a tool hop while claiming a complete path.

## Prerequisites

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Option A — CLI only (fastest)

```bash
witnessdiff compare \
  fixtures/evidence/silent-omission.reference.json \
  fixtures/evidence/silent-omission.evidence.json
```

Expected: `COMPLETENESS_OVERCLAIM` — reference has four hops, evidence attests three, export claims `complete_path`.

Then run the full regression matrix:

```bash
witnessdiff run-all-suites
```

Expected: **15 evidence + 10 behavioral = 25** scenarios, all passing against committed baselines.

## Option B — API + viewer (recommended for screen recording)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Viewer | http://localhost:5173 |
| API | http://localhost:8080 |

1. Open the viewer and click **Load demo run** (calls `POST /v1/demo/silent-omission`).
2. Inspect the side-by-side reference vs evidence hop table and verdict banner.
3. Optional: run `./scripts/demo.sh` in another terminal for CLI + suite output.

## Recording a GIF

We do not commit binary GIFs to the repo. To capture one for README or LinkedIn:

```bash
# Terminal recording (asciinema)
asciinema rec witnessdiff-demo.cast
./scripts/demo.sh
# Upload to asciinema.org or convert with agg/svg-term

# Or record the viewer in Docker with peek, LICEcap, or OBS (90s target)
```

Suggested narrative (≈90s):

1. **Problem** — "Agent ran four MCP tools; export shows three and says complete."
2. **Compare** — Run demo endpoint or CLI compare; show `COMPLETENESS_OVERCLAIM`.
3. **Regression** — `witnessdiff run-all-suites` → 25/25 green in CI.
4. **Boundary** — Reference trace is the oracle you supply; WitnessDiff tests export vs that reference.

## Public deploy

See [DEPLOY.md](DEPLOY.md) for Render blueprint and environment variables.

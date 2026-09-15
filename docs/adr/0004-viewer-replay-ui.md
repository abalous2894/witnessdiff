# ADR 0004: Viewer replay UI

## Status

Accepted — 2026-03-24

## Context

Week 5 requires a recruiter-friendly demo surface that shows witness-integrity failures visually, not only as CLI JSON.

## Decision

- Ship a Vite + React viewer under `apps/viewer/`
- Side-by-side reference trace vs evidence bundle with hop highlighting from `report.findings`
- Add `POST /v1/demo/silent-omission` to seed the canonical failure case without local fixtures
- Enable CORS on the API for dev and static deploys
- Serve viewer via nginx in Docker Compose with reverse proxy to the API

## Consequences

- Public demo can be a static viewer + hosted API
- Week 6 focuses on polish (demo GIF, expanded docs) rather than new backend surfaces

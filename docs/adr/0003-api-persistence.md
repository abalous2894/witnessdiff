# ADR 0003: API persistence layer

## Status

Accepted — 2026-03-24

## Context

Week 4 requires a deployable service that persists comparison runs for replay and demo hosting.

## Decision

- Add `witnessdiff.api` FastAPI module with Postgres and in-memory stores
- Use `DATABASE_URL` to select Postgres; default to in-memory for local dev and CI tests
- Ship `docker compose up` with Postgres 16 and API on port 8080
- Expose `witnessdiff serve` CLI command wrapping uvicorn

## Consequences

- CI tests use in-memory store via `create_app(store=InMemoryRunStore())`
- Production demos should set `DATABASE_URL` for durable run history
- Week 5 viewer can consume `/v1/runs/{id}` without new backend work

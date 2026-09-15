# Architecture (week 1)

```text
┌─────────────────────┐     ┌─────────────────────┐
│  Reference trace    │     │  Evidence bundle    │
│  (instrumented)     │     │  (export under test)│
└─────────┬───────────┘     └──────────┬──────────┘
          │                            │
          v                            v
   trace_parser                 claim_parser
          │                            │
          └────────────┬───────────────┘
                       v
              witness_integrity comparator
                       │
                       v
              comparison-report/v1
                       │
          ┌────────────┴────────────┐
          v                         v
     CLI / pytest              (future: API + viewer)
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `trace_parser` | Load and validate reference traces |
| `claim_parser` | Load and validate evidence bundles |
| `comparators.witness_integrity` | Hop matching, findings, verdict |
| `suite` | Fixture discovery and regression runner |
| `cli` | Typer commands for local use and CI |

## API layer (week 4)

```text
POST /v1/compare ──► witnessdiff.api.service ──► PostgresRunStore / InMemoryRunStore
GET  /v1/runs    ──► list persisted comparison reports
```

`DATABASE_URL` selects Postgres; otherwise the API uses an in-memory store.

## Planned additions

- `apps/viewer` — Minimal replay UI (week 5)

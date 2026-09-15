# ADR 0002: Witness comparator expansion

## Status

Accepted — 2026-03-24

## Context

Week 1–2 comparators covered silent omission, reordering, and complete paths. Integrators also need detection of binding substitution, inflated `declared_count`, extra export hops, and partial-path omissions without overclaiming.

## Decision

Expand `compare_witness_integrity` with:

1. `arguments_digest_mismatch` — same anchor, different argument binding
2. `declared_count_mismatch` — export count claims diverge from attested or reference hops
3. Relaxed bundle parsing — allow `declared_count` greater than attested actions; comparator flags it
4. Verdict priority — `declared_count_mismatch` under `complete_path` maps to `COMPLETENESS_OVERCLAIM`

## Consequences

- Evidence fixtures can model real export bugs that still parse as JSON
- `EXPORT_TRUNCATION` cases use non-complete claims when isolating extra-hop behavior
- Week 3 fixture corpus reaches 10 evidence + 5 behavioral = 15 total cases

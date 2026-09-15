# ADR 0001: Neutral public schemas

## Status

Accepted — 2026-03-24

## Context

WitnessDiff applies expertise adjacent to agent evidence systems. The public repository must not ship proprietary schemas, receipt formats, or test vectors from other products.

## Decision

Publish neutral schemas:

- `witnessdiff.reference-trace/v1`
- `witnessdiff.evidence-bundle/v1`
- `witnessdiff.comparison-report/v1`

Use WitnessDiff-native verdict labels (`WITNESS_OMISSION`, `COMPLETENESS_OVERCLAIM`, etc.) in all user-facing output.

## Consequences

- Integrators map their exports via adapters (future work).
- Documentation may note conceptual alignment with hop-set completeness literature without importing foreign schema IDs.
- Aevesa-specific terminology remains out of this repository.

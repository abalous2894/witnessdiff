# Threat model (v1)

## Scope

WitnessDiff v1 compares synthetic or sandbox **reference traces** with **evidence bundles** supplied to the tool. It does not secure a production agent runtime.

## Trust assumptions

| Asset | Assumption |
|-------|------------|
| Reference trace | Trusted for the test scenario (instrumented runner, synthetic capture) |
| Evidence bundle | Untrusted declarative export under test |
| WitnessDiff engine | Correctly implements deterministic comparison rules |

## Out of scope (v1)

- Proving runtime behavior from uninstrumented logs
- Cryptographic tamper evidence or Merkle verification
- Detecting adversarial collusion between reference capture and export pipeline
- MCP server authentication or live tool execution

## Fail-closed behavior

- Schema validation errors reject input (`INVALID_INPUT`)
- Session ID mismatch rejects comparison
- CI exits non-zero when any fixture regresses

## Non-goals

WitnessDiff is not a replacement for platform audit logs, SIEM correlation, or independent cryptographic prove layers. It is a **regression lab** for export fidelity relative to a reference you already trust for the test.

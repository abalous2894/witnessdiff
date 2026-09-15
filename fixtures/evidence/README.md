# Evidence-integrity fixtures

Each case is a triple: `*.reference.json`, `*.evidence.json`, `*.expected.json`.

| Fixture | Verdict | Failure mode |
|---------|---------|--------------|
| `complete-path` | `COMPLETE` | Happy path |
| `silent-omission` | `COMPLETENESS_OVERCLAIM` | Missing hop under complete claim |
| `reordered-tool-call` | `MISMATCH` | Same hops, wrong order |
| `action-id-substitution` | `MISMATCH` | Swapped ledger anchor |
| `extra-hop-in-export` | `EXPORT_TRUNCATION` | Export adds unattested hop |
| `declared-count-overclaim` | `COMPLETENESS_OVERCLAIM` | `declared_count` exceeds witness |
| `partial-path-omission` | `WITNESS_OMISSION` | Omission without complete claim |
| `arguments-digest-mismatch` | `MISMATCH` | Same anchor, different args digest |
| `fabricated-export-hop` | `EXPORT_TRUNCATION` | Prohibited tool in export |
| `unknown-claim-omission` | `WITNESS_OMISSION` | Omission with unknown completeness |

Run:

```bash
witnessdiff run-evidence-suite
```

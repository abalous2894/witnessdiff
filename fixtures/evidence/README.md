# Evidence-integrity fixtures

Each case is a triple: `*.reference.json`, `*.evidence.json`, `*.expected.json`.

| Fixture | Verdict | Failure mode |
|---------|---------|--------------|
| `complete-path` | `COMPLETE` | Happy path |
| `two-hop-complete` | `COMPLETE` | Minimal two-hop match |
| `matching-four-hop-complete` | `COMPLETE` | Full four-hop refund path |
| `silent-omission` | `COMPLETENESS_OVERCLAIM` | Missing hop under complete claim |
| `declared-count-overclaim` | `COMPLETENESS_OVERCLAIM` | `declared_count` exceeds witness |
| `declared-internal-gap` | `COMPLETENESS_OVERCLAIM` | `declared_count` exceeds attested actions |
| `reordered-tool-call` | `MISMATCH` | Same hops, wrong order |
| `action-id-substitution` | `MISMATCH` | Swapped ledger anchor |
| `tool-name-at-index` | `MISMATCH` | Wrong tool at same index |
| `arguments-digest-mismatch` | `MISMATCH` | Same anchor, different args digest |
| `partial-path-omission` | `WITNESS_OMISSION` | Omission without complete claim |
| `truncated-tail-omission` | `WITNESS_OMISSION` | Export stops after first hop |
| `unknown-claim-omission` | `WITNESS_OMISSION` | Omission with unknown completeness |
| `extra-hop-in-export` | `EXPORT_TRUNCATION` | Export adds unattested hop |
| `fabricated-export-hop` | `EXPORT_TRUNCATION` | Prohibited tool in export |

Run:

```bash
witnessdiff run-evidence-suite
```

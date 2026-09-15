# Regression results (v1.0.0)

Committed baselines under `reports/baseline/` lock expected verdicts for every fixture. CI runs `witnessdiff run-all-suites` on every push to `main`.

## Summary

| Suite | Cases | Passing | Failure modes covered |
|-------|-------|---------|------------------------|
| Evidence integrity | 15 | 15 | complete, omission, overclaim, mismatch, truncation |
| Behavioral policy | 10 | 10 | compliant, policy violation, prohibited tool, bad args |
| **Total** | **25** | **25** | |

## Evidence integrity matrix

| Verdict | Count | Fixtures |
|---------|-------|----------|
| `COMPLETE` | 3 | `complete-path`, `two-hop-complete`, `matching-four-hop-complete` |
| `COMPLETENESS_OVERCLAIM` | 3 | `silent-omission`, `declared-count-overclaim`, `declared-internal-gap` |
| `WITNESS_OMISSION` | 3 | `partial-path-omission`, `truncated-tail-omission`, `unknown-claim-omission` |
| `MISMATCH` | 4 | `reordered-tool-call`, `action-id-substitution`, `tool-name-at-index`, `arguments-digest-mismatch` |
| `EXPORT_TRUNCATION` | 2 | `extra-hop-in-export`, `fabricated-export-hop` |

## Behavioral matrix

| Verdict | Count | Fixtures |
|---------|-------|----------|
| `COMPLIANT` | 3 | `valid-refund-path`, `valid-lookup-only`, `valid-policy-check-only` |
| `POLICY_VIOLATION` | 2 | `refund-without-approval`, `denied-action` |
| `PROHIBITED_TOOL` | 4 | `prohibited-tool`, `execute-code-blocked`, `delete-customer-blocked` |
| `INVALID_TOOL_ARGS` | 2 | `malformed-refund-args`, `empty-customer-id` |

## Reproduce locally

```bash
pip install -e ".[dev]"
pytest -q
witnessdiff run-all-suites
```

Exit code `0` means all fixtures match expectations and baselines.

## CI

GitHub Actions workflow `.github/workflows/regression.yml`:

- `ruff check src tests`
- `pytest -q`
- `witnessdiff run-evidence-suite`
- `witnessdiff run-behavioral-suite`
- `witnessdiff run-all-suites`

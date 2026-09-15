# Evaluation methodology

WitnessDiff separates **behavioral** evaluation from **witness-integrity** evaluation. Week 1 ships the witness-integrity lane only.

## Witness-integrity lane

**Inputs**

1. `witnessdiff.reference-trace/v1` — instrumented reference trace (trusted for the test)
2. `witnessdiff.evidence-bundle/v1` — exported bundle with an explicit `completeness_claim`

**Process**

1. Parse and validate both documents (Pydantic models).
2. Match actions by `(tool_name, action_id)` when `action_id` is present; otherwise by tool name membership.
3. Compare positional alignment for the shared prefix length.
4. Emit structured findings and a single verdict.

## Verdict labels

| Verdict | When it fires |
|---------|----------------|
| `COMPLETE` | Reference and evidence describe the same hop set |
| `WITNESS_OMISSION` | Reference contains unattested hops; export does not claim full completeness |
| `COMPLETENESS_OVERCLAIM` | Export claims `complete_path` but omits reference hops |
| `EXPORT_TRUNCATION` | Evidence attests hops absent from the reference |
| `MISMATCH` | Tool identity, binding, or order diverges |
| `INVALID_INPUT` | Session mismatch or schema validation failure |

## Oracle alignment note

These labels are **WitnessDiff-native**. They intentionally avoid proprietary schema names.

Conceptual mapping for readers familiar with hop-set completeness literature:

| WitnessDiff | Typical hop-set oracle direction |
|-------------|----------------------------------|
| `WITNESS_OMISSION` / `COMPLETENESS_OVERCLAIM` | Reference path has hops not attested in export |
| `EXPORT_TRUNCATION` | Export attests hops not present in reference |

## Deterministic vs model-based graders

Witness-integrity checks are **fully deterministic**. Behavioral graders (week 2+) will also default to deterministic policy and schema checks. Any optional LLM judge will be documented separately and never mixed into CI pass/fail without an explicit flag.

## Coverage guidance

OpenAI’s eval guidance recommends small, representative datasets (often 10–50 cases) with coverage over raw volume. WitnessDiff v1 targets **25 total fixtures** across both lanes, prioritizing failure modes integrators actually miss: silent omission, reordering, substitution, and completeness overclaims.

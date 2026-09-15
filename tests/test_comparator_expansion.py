from pathlib import Path

import pytest

from witnessdiff.claim_parser import load_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.models import WitnessVerdict
from witnessdiff.suite import discover_evidence_fixtures, run_evidence_case
from witnessdiff.trace_parser import load_reference_trace

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "evidence"


@pytest.mark.parametrize(
    "name",
    [
        "declared-count-overclaim",
        "partial-path-omission",
        "arguments-digest-mismatch",
        "extra-hop-in-export",
        "fabricated-export-hop",
        "unknown-claim-omission",
        "action-id-substitution",
    ],
)
def test_week3_evidence_fixtures(name: str):
    case = next(c for c in discover_evidence_fixtures(FIXTURES) if c.name == name)
    report, expected = run_evidence_case(case)
    assert report.ok == expected["ok"]
    assert report.verdict.value == expected["verdict"]


def test_declared_count_findings_present():
    reference = load_reference_trace(FIXTURES / "declared-count-overclaim.reference.json")
    evidence = load_evidence_bundle(FIXTURES / "declared-count-overclaim.evidence.json")
    report = compare_witness_integrity(reference, evidence)
    assert report.verdict == WitnessVerdict.COMPLETENESS_OVERCLAIM
    assert any(f.kind == "declared_count_mismatch" for f in report.findings)


def test_arguments_digest_mismatch_finding():
    reference = load_reference_trace(FIXTURES / "arguments-digest-mismatch.reference.json")
    evidence = load_evidence_bundle(FIXTURES / "arguments-digest-mismatch.evidence.json")
    report = compare_witness_integrity(reference, evidence)
    assert report.verdict == WitnessVerdict.MISMATCH
    assert any(f.kind == "arguments_digest_mismatch" for f in report.findings)

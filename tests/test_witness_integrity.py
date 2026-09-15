from pathlib import Path

import pytest

from witnessdiff.claim_parser import load_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.models import WitnessVerdict
from witnessdiff.suite import assert_case_matches, discover_evidence_fixtures, run_evidence_case
from witnessdiff.trace_parser import load_reference_trace

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "evidence"


def test_silent_omission_flags_completeness_overclaim():
    reference = load_reference_trace(FIXTURES / "silent-omission.reference.json")
    evidence = load_evidence_bundle(FIXTURES / "silent-omission.evidence.json")
    report = compare_witness_integrity(reference, evidence)

    assert report.ok is False
    assert report.verdict == WitnessVerdict.COMPLETENESS_OVERCLAIM
    assert report.reference_action_count == 4
    assert report.evidence_action_count == 3
    assert any(finding.kind == "missing_in_evidence" for finding in report.findings)


def test_reordered_tool_call_is_mismatch():
    reference = load_reference_trace(FIXTURES / "reordered-tool-call.reference.json")
    evidence = load_evidence_bundle(FIXTURES / "reordered-tool-call.evidence.json")
    report = compare_witness_integrity(reference, evidence)

    assert report.ok is False
    assert report.verdict == WitnessVerdict.MISMATCH


def test_complete_path_passes():
    reference = load_reference_trace(FIXTURES / "complete-path.reference.json")
    evidence = load_evidence_bundle(FIXTURES / "complete-path.evidence.json")
    report = compare_witness_integrity(reference, evidence)

    assert report.ok is True
    assert report.verdict == WitnessVerdict.COMPLETE
    assert report.findings == []


@pytest.mark.parametrize("case", discover_evidence_fixtures(FIXTURES), ids=lambda case: case.name)
def test_evidence_fixtures_match_expected(case):
    report, expected = run_evidence_case(case)
    errors = assert_case_matches(report, expected)
    assert errors == []

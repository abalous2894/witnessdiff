from pathlib import Path

from witnessdiff.behavioral_suite import run_behavioral_suite
from witnessdiff.reports import compare_to_baseline, load_suite_baseline
from witnessdiff.suite import run_evidence_suite

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "reports" / "baseline"


def test_behavioral_suite_matches_committed_baseline():
    _, failed, _, case_results = run_behavioral_suite(ROOT / "fixtures" / "behavioral")
    assert failed == 0
    baseline = load_suite_baseline(BASELINE / "behavioral.json")
    errors = compare_to_baseline(case_results, baseline)
    assert errors == []


def test_evidence_suite_matches_committed_baseline():
    _, failed, _, case_results = run_evidence_suite(ROOT / "fixtures" / "evidence")
    assert failed == 0
    baseline = load_suite_baseline(BASELINE / "evidence.json")
    errors = compare_to_baseline(case_results, baseline)
    assert errors == []

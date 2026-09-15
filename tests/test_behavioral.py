import json
from pathlib import Path

import pytest

from witnessdiff.behavioral_suite import (
    assert_behavioral_matches,
    discover_behavioral_fixtures,
    run_behavioral_case,
)
from witnessdiff.graders.behavioral import grade_behavioral_scenario, parse_behavioral_scenario
from witnessdiff.models import BehavioralVerdict

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "behavioral"


def test_refund_without_approval_violates_policy():
    path = FIXTURES / "refund-without-approval.scenario.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    scenario = parse_behavioral_scenario(raw)
    report = grade_behavioral_scenario(scenario)

    assert report.ok is False
    assert report.verdict == BehavioralVerdict.POLICY_VIOLATION
    assert any(finding.kind == "approval_required" for finding in report.findings)


def test_prohibited_tool_detected():
    raw = json.loads((FIXTURES / "prohibited-tool.scenario.json").read_text(encoding="utf-8"))
    scenario = parse_behavioral_scenario(raw)
    report = grade_behavioral_scenario(scenario)

    assert report.verdict == BehavioralVerdict.PROHIBITED_TOOL


@pytest.mark.parametrize(
    "case", discover_behavioral_fixtures(FIXTURES), ids=lambda case: case.name
)
def test_behavioral_fixtures_match_expected(case):
    report, expected = run_behavioral_case(case)
    errors = assert_behavioral_matches(report, expected)
    assert errors == []

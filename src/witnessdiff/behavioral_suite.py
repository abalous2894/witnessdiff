from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from witnessdiff.graders.behavioral import grade_behavioral_scenario, parse_behavioral_scenario
from witnessdiff.models import BehavioralReport


@dataclass(frozen=True)
class BehavioralFixtureCase:
    name: str
    scenario_path: Path
    expected_path: Path


def discover_behavioral_fixtures(fixtures_dir: Path) -> list[BehavioralFixtureCase]:
    scenarios = sorted(fixtures_dir.glob("*.scenario.json"))
    cases: list[BehavioralFixtureCase] = []
    for scenario_path in scenarios:
        stem = scenario_path.name.removesuffix(".scenario.json")
        expected_path = fixtures_dir / f"{stem}.expected.json"
        if expected_path.exists():
            cases.append(
                BehavioralFixtureCase(
                    name=stem,
                    scenario_path=scenario_path,
                    expected_path=expected_path,
                )
            )
    return cases


def run_behavioral_case(case: BehavioralFixtureCase) -> tuple[BehavioralReport, dict[str, Any]]:
    raw = json.loads(case.scenario_path.read_text(encoding="utf-8"))
    scenario = parse_behavioral_scenario(raw)
    report = grade_behavioral_scenario(scenario)
    expected = json.loads(case.expected_path.read_text(encoding="utf-8"))
    return report, expected


def assert_behavioral_matches(report: BehavioralReport, expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("ok", "verdict", "session_id", "scenario_name"):
        actual = getattr(report, field)
        exp = expected.get(field)
        if exp is not None and actual != exp and str(actual) != str(exp):
            errors.append(f"{field}: expected {exp!r}, got {actual!r}")
    return errors


def run_behavioral_suite(
    fixtures_dir: Path,
) -> tuple[int, int, list[str], dict[str, dict[str, Any]]]:
    passed = 0
    failed = 0
    messages: list[str] = []
    case_results: dict[str, dict[str, Any]] = {}
    cases = discover_behavioral_fixtures(fixtures_dir)
    if not cases:
        return 0, 1, ["no behavioral fixtures discovered"], case_results

    for case in cases:
        report, expected = run_behavioral_case(case)
        errors = assert_behavioral_matches(report, expected)
        case_results[case.name] = {
            "ok": report.ok,
            "verdict": report.verdict.value,
            "session_id": report.session_id,
            "finding_count": len(report.findings),
        }
        if errors:
            failed += 1
            messages.append(f"FAIL {case.name}: " + "; ".join(errors))
        else:
            passed += 1
            messages.append(f"PASS {case.name}: {report.verdict.value}")

    return passed, failed, messages, case_results

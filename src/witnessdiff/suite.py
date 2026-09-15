from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from witnessdiff.claim_parser import load_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.models import ComparisonReport, WitnessVerdict
from witnessdiff.trace_parser import load_reference_trace


@dataclass(frozen=True)
class EvidenceFixtureCase:
    name: str
    reference_path: Path
    evidence_path: Path
    expected_path: Path


def discover_evidence_fixtures(fixtures_dir: Path) -> list[EvidenceFixtureCase]:
    references = sorted(fixtures_dir.glob("*.reference.json"))
    cases: list[EvidenceFixtureCase] = []
    for reference_path in references:
        stem = reference_path.name.removesuffix(".reference.json")
        evidence_path = fixtures_dir / f"{stem}.evidence.json"
        expected_path = fixtures_dir / f"{stem}.expected.json"
        if evidence_path.exists() and expected_path.exists():
            cases.append(
                EvidenceFixtureCase(
                    name=stem,
                    reference_path=reference_path,
                    evidence_path=evidence_path,
                    expected_path=expected_path,
                )
            )
    return cases


def run_evidence_case(case: EvidenceFixtureCase) -> tuple[ComparisonReport, dict]:
    reference = load_reference_trace(case.reference_path)
    evidence = load_evidence_bundle(case.evidence_path)
    report = compare_witness_integrity(reference, evidence)
    expected = json.loads(case.expected_path.read_text(encoding="utf-8"))
    return report, expected


def assert_case_matches(report: ComparisonReport, expected: dict) -> list[str]:
    errors: list[str] = []
    for field in (
        "ok",
        "verdict",
        "reference_action_count",
        "evidence_action_count",
        "completeness_claim",
        "session_id",
    ):
        actual = getattr(report, field)
        exp = expected.get(field)
        if exp is not None and actual != exp and str(actual) != str(exp):
            errors.append(f"{field}: expected {exp!r}, got {actual!r}")
    return errors


def run_evidence_suite(fixtures_dir: Path) -> tuple[int, int, list[str]]:
    passed = 0
    failed = 0
    messages: list[str] = []
    cases = discover_evidence_fixtures(fixtures_dir)
    if not cases:
        return 0, 1, ["no evidence fixtures discovered"]

    for case in cases:
        report, expected = run_evidence_case(case)
        errors = assert_case_matches(report, expected)
        if errors:
            failed += 1
            messages.append(f"FAIL {case.name}: " + "; ".join(errors))
        else:
            passed += 1
            messages.append(f"PASS {case.name}: {report.verdict.value}")

    return passed, failed, messages

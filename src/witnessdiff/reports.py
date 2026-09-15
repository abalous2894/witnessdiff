from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from witnessdiff.models import SuiteBaseline, SuiteCaseBaseline, SuiteRunSummary

SuiteName = Literal["behavioral", "evidence"]


def build_suite_summary(
    suite: SuiteName,
    case_results: dict[str, dict[str, Any]],
    passed: int,
    failed: int,
) -> SuiteRunSummary:
    return SuiteRunSummary(
        suite=suite,
        passed=passed,
        failed=failed,
        cases=case_results,
    )


def write_suite_report(summary: SuiteRunSummary, output_path: Path) -> None:
    payload = summary.model_dump(mode="json", by_alias=True)
    payload["generated_at"] = datetime.now(tz=UTC).isoformat()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_suite_baseline(path: Path) -> SuiteBaseline:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return SuiteBaseline.model_validate(raw)


def compare_to_baseline(
    case_results: dict[str, dict[str, Any]],
    baseline: SuiteBaseline,
) -> list[str]:
    errors: list[str] = []
    for name, expected in baseline.cases.items():
        actual = case_results.get(name)
        if actual is None:
            errors.append(f"missing case in run: {name}")
            continue
        if actual.get("ok") != expected.ok:
            errors.append(f"{name}.ok: expected {expected.ok!r}, got {actual.get('ok')!r}")
        if str(actual.get("verdict")) != expected.verdict:
            errors.append(
                f"{name}.verdict: expected {expected.verdict!r}, got {actual.get('verdict')!r}"
            )

    extra = set(case_results) - set(baseline.cases)
    for name in sorted(extra):
        errors.append(f"unexpected case not in baseline: {name}")
    return errors


def baseline_from_case_results(
    suite: SuiteName,
    case_results: dict[str, dict[str, Any]],
) -> SuiteBaseline:
    cases = {
        name: SuiteCaseBaseline(ok=bool(result["ok"]), verdict=str(result["verdict"]))
        for name, result in case_results.items()
    }
    return SuiteBaseline(suite=suite, cases=cases)


def write_baseline(baseline: SuiteBaseline, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(baseline.model_dump(mode="json", by_alias=True), indent=2) + "\n"
    output_path.write_text(text, encoding="utf-8")

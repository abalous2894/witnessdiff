from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from witnessdiff.api.schemas import ComparisonRunDetail, ComparisonRunSummary, SuiteRunResponse
from witnessdiff.api.store import RunStore, StoredComparisonRun
from witnessdiff.behavioral_suite import run_behavioral_suite
from witnessdiff.claim_parser import parse_evidence_bundle
from witnessdiff.comparators import compare_witness_integrity
from witnessdiff.suite import run_evidence_suite
from witnessdiff.trace_parser import parse_reference_trace


def run_and_persist_comparison(
    store: RunStore,
    reference: dict[str, Any],
    evidence: dict[str, Any],
) -> ComparisonRunDetail:
    ref = parse_reference_trace(reference)
    ev = parse_evidence_bundle(evidence)
    report = compare_witness_integrity(ref, ev)
    report_json = report.model_dump(mode="json", by_alias=True)

    stored = store.save_comparison(
        session_id=report.session_id,
        ok=report.ok,
        verdict=report.verdict.value,
        reference_action_count=report.reference_action_count,
        evidence_action_count=report.evidence_action_count,
        completeness_claim=report.completeness_claim,
        reference_json=reference,
        evidence_json=evidence,
        report_json=report_json,
    )
    return _to_detail(stored)


def get_comparison_run(store: RunStore, run_id: UUID) -> ComparisonRunDetail | None:
    stored = store.get_comparison(run_id)
    if stored is None:
        return None
    return _to_detail(stored)


def list_comparison_runs(store: RunStore, limit: int = 50) -> list[ComparisonRunSummary]:
    return [_to_summary(stored) for stored in store.list_comparisons(limit=limit)]


def run_suite(fixtures_root: Path, suite: str) -> SuiteRunResponse:
    if suite == "evidence":
        passed, failed, messages, _ = run_evidence_suite(fixtures_root / "evidence")
    elif suite == "behavioral":
        passed, failed, messages, _ = run_behavioral_suite(fixtures_root / "behavioral")
    else:
        raise ValueError(f"unsupported suite: {suite}")

    return SuiteRunResponse(suite=suite, passed=passed, failed=failed, messages=messages)


def _to_summary(stored: StoredComparisonRun) -> ComparisonRunSummary:
    return ComparisonRunSummary(
        id=stored.id,
        session_id=stored.session_id,
        ok=stored.ok,
        verdict=stored.verdict,
        reference_action_count=stored.reference_action_count,
        evidence_action_count=stored.evidence_action_count,
        completeness_claim=stored.completeness_claim,
        created_at=stored.created_at,
    )


def _to_detail(stored: StoredComparisonRun) -> ComparisonRunDetail:
    return ComparisonRunDetail(
        id=stored.id,
        session_id=stored.session_id,
        ok=stored.ok,
        verdict=stored.verdict,
        reference_action_count=stored.reference_action_count,
        evidence_action_count=stored.evidence_action_count,
        completeness_claim=stored.completeness_claim,
        created_at=stored.created_at,
        reference=stored.reference_json,
        evidence=stored.evidence_json,
        report=stored.report_json,
    )

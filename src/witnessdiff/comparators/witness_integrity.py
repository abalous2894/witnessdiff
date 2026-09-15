from __future__ import annotations

from witnessdiff.models import (
    ComparisonReport,
    EvidenceBundle,
    HopFinding,
    ReferenceTrace,
    WitnessVerdict,
)


def _action_key(tool_name: str, action_id: str | None) -> tuple[str, str | None]:
    return (tool_name.strip().lower(), action_id)


def compare_witness_integrity(
    reference: ReferenceTrace,
    evidence: EvidenceBundle,
) -> ComparisonReport:
    if reference.session_id != evidence.session_id:
        return ComparisonReport(
            session_id=reference.session_id,
            ok=False,
            verdict=WitnessVerdict.INVALID_INPUT,
            reference_action_count=len(reference.actions),
            evidence_action_count=len(evidence.actions),
            completeness_claim=evidence.completeness_claim,
            findings=[
                HopFinding(
                    kind="order_mismatch",
                    detail=(
                        f"session_id mismatch: reference={reference.session_id!r} "
                        f"evidence={evidence.session_id!r}"
                    ),
                )
            ],
            note="Reference trace and evidence bundle must describe the same session.",
        )

    findings: list[HopFinding] = []

    ref_by_key: dict[tuple[str, str | None], list[int]] = {}
    for action in reference.actions:
        key = _action_key(action.tool_name, action.action_id)
        ref_by_key.setdefault(key, []).append(action.index)

    ev_by_key: dict[tuple[str, str | None], list[int]] = {}
    for action in evidence.actions:
        key = _action_key(action.tool_name, action.action_id)
        ev_by_key.setdefault(key, []).append(action.index)

    ref_keys = set(ref_by_key)
    ev_keys = set(ev_by_key)

    missing_in_evidence = ref_keys - ev_keys
    missing_in_reference = ev_keys - ref_keys

    for key in sorted(missing_in_evidence):
        tool_name, action_id = key
        for ref_index in ref_by_key[key]:
            findings.append(
                HopFinding(
                    kind="missing_in_evidence",
                    reference_index=ref_index,
                    tool_name=tool_name,
                    detail=(
                        "Reference action not attested in evidence bundle"
                        + (f" (action_id={action_id})" if action_id else "")
                    ),
                )
            )

    for key in sorted(missing_in_reference):
        tool_name, action_id = key
        for ev_index in ev_by_key[key]:
            findings.append(
                HopFinding(
                    kind="missing_in_reference",
                    evidence_index=ev_index,
                    tool_name=tool_name,
                    detail=(
                        "Evidence bundle attests action absent from reference trace"
                        + (f" (action_id={action_id})" if action_id else "")
                    ),
                )
            )

    shared = ref_keys & ev_keys
    pair_len = min(len(reference.actions), len(evidence.actions))
    for index in range(pair_len):
        ref_action = reference.actions[index]
        ev_action = evidence.actions[index]
        if ref_action.tool_name.strip().lower() != ev_action.tool_name.strip().lower():
            findings.append(
                HopFinding(
                    kind="tool_name_mismatch",
                    reference_index=ref_action.index,
                    evidence_index=ev_action.index,
                    tool_name=ref_action.tool_name,
                    detail=(
                        f"Position {index}: reference tool {ref_action.tool_name!r} "
                        f"!= evidence tool {ev_action.tool_name!r}"
                    ),
                )
            )
        if ref_action.action_id and ev_action.action_id and ref_action.action_id != ev_action.action_id:
            findings.append(
                HopFinding(
                    kind="action_id_mismatch",
                    reference_index=ref_action.index,
                    evidence_index=ev_action.index,
                    tool_name=ref_action.tool_name,
                    detail=(
                        f"Position {index}: action_id mismatch for tool {ref_action.tool_name!r}"
                    ),
                )
            )

    for key in shared:
        if ref_by_key[key] != ev_by_key[key]:
            findings.append(
                HopFinding(
                    kind="order_mismatch",
                    tool_name=key[0],
                    detail=(
                        f"Action order differs for tool {key[0]!r}: "
                        f"reference indices {ref_by_key[key]} vs evidence indices {ev_by_key[key]}"
                    ),
                )
            )

    verdict = _derive_verdict(findings, reference, evidence)
    ok = verdict == WitnessVerdict.COMPLETE
    note = _build_note(verdict, findings, reference, evidence)

    return ComparisonReport(
        session_id=reference.session_id,
        ok=ok,
        verdict=verdict,
        reference_action_count=len(reference.actions),
        evidence_action_count=len(evidence.actions),
        completeness_claim=evidence.completeness_claim,
        findings=findings,
        note=note,
    )


def _derive_verdict(
    findings: list[HopFinding],
    reference: ReferenceTrace,
    evidence: EvidenceBundle,
) -> WitnessVerdict:
    kinds = {finding.kind for finding in findings}
    has_missing_in_evidence = "missing_in_evidence" in kinds
    has_missing_in_reference = "missing_in_reference" in kinds
    has_mismatch = bool(kinds & {"tool_name_mismatch", "action_id_mismatch", "order_mismatch"})

    if has_missing_in_evidence and has_missing_in_reference:
        return WitnessVerdict.MISMATCH
    if has_mismatch and not has_missing_in_evidence and not has_missing_in_reference:
        return WitnessVerdict.MISMATCH
    if has_missing_in_evidence:
        if evidence.completeness_claim == "complete_path":
            return WitnessVerdict.COMPLETENESS_OVERCLAIM
        return WitnessVerdict.WITNESS_OMISSION
    if has_missing_in_reference:
        return WitnessVerdict.EXPORT_TRUNCATION
    if has_mismatch:
        return WitnessVerdict.MISMATCH
    if len(reference.actions) != len(evidence.actions):
        if len(reference.actions) > len(evidence.actions):
            return (
                WitnessVerdict.COMPLETENESS_OVERCLAIM
                if evidence.completeness_claim == "complete_path"
                else WitnessVerdict.WITNESS_OMISSION
            )
        return WitnessVerdict.EXPORT_TRUNCATION
    return WitnessVerdict.COMPLETE


def _build_note(
    verdict: WitnessVerdict,
    findings: list[HopFinding],
    reference: ReferenceTrace,
    evidence: EvidenceBundle,
) -> str:
    if verdict == WitnessVerdict.COMPLETE:
        return "Evidence bundle faithfully represents the reference trace hop set."

    omission_count = sum(1 for finding in findings if finding.kind == "missing_in_evidence")
    if verdict == WitnessVerdict.COMPLETENESS_OVERCLAIM:
        return (
            f"Export claims completeness ({evidence.completeness_claim}) but reference contains "
            f"{len(reference.actions)} action(s) and evidence contains {len(evidence.actions)}; "
            f"{omission_count} reference hop(s) are not attested."
        )

    if verdict == WitnessVerdict.WITNESS_OMISSION:
        return (
            f"Reference trace contains {len(reference.actions)} action(s); evidence attests "
            f"{len(evidence.actions)}. {omission_count} hop(s) omitted from export."
        )

    if verdict == WitnessVerdict.EXPORT_TRUNCATION:
        extra = sum(1 for finding in findings if finding.kind == "missing_in_reference")
        return f"Evidence attests {extra} hop(s) not present in the reference trace."

    return "Reference trace and evidence bundle diverge by tool identity, binding, or order."

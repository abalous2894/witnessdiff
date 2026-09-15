from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

REFERENCE_TRACE_SCHEMA = "witnessdiff.reference-trace/v1"
EVIDENCE_BUNDLE_SCHEMA = "witnessdiff.evidence-bundle/v1"
COMPARISON_REPORT_SCHEMA = "witnessdiff.comparison-report/v1"
BEHAVIORAL_SCENARIO_SCHEMA = "witnessdiff.behavioral-scenario/v1"
BEHAVIORAL_REPORT_SCHEMA = "witnessdiff.behavioral-report/v1"
SUITE_BASELINE_SCHEMA = "witnessdiff.suite-baseline/v1"


class WitnessVerdict(StrEnum):
    COMPLETE = "COMPLETE"
    WITNESS_OMISSION = "WITNESS_OMISSION"
    EXPORT_TRUNCATION = "EXPORT_TRUNCATION"
    MISMATCH = "MISMATCH"
    COMPLETENESS_OVERCLAIM = "COMPLETENESS_OVERCLAIM"
    INVALID_INPUT = "INVALID_INPUT"


class TraceAction(BaseModel):
    index: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    action_id: str | None = None
    arguments_digest: str | None = None
    verdict: str | None = None

    @field_validator("action_id", "arguments_digest")
    @classmethod
    def normalize_hex(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class ReferenceTrace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.reference-trace/v1"] = Field(alias="schema")
    session_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    captured_at: str | None = None
    actions: list[TraceAction] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_contiguous_indices(self) -> ReferenceTrace:
        indices = [action.index for action in self.actions]
        expected = list(range(len(self.actions)))
        if sorted(indices) != expected:
            raise ValueError("reference trace action indices must be contiguous starting at 0")
        return self


class EvidenceAction(BaseModel):
    index: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    action_id: str | None = None
    arguments_digest: str | None = None

    @field_validator("action_id", "arguments_digest")
    @classmethod
    def normalize_hex(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.evidence-bundle/v1"] = Field(alias="schema")
    session_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    exported_at: str | None = None
    completeness_claim: Literal["complete_path", "partial_path", "unknown"]
    declared_count: int | None = Field(default=None, ge=0)
    actions: list[EvidenceAction]

    @model_validator(mode="after")
    def validate_declared_count(self) -> EvidenceBundle:
        if self.declared_count is not None and self.declared_count < len(self.actions):
            raise ValueError("declared_count cannot be less than the number of attested actions")
        return self


class HopFinding(BaseModel):
    kind: Literal[
        "missing_in_evidence",
        "missing_in_reference",
        "tool_name_mismatch",
        "action_id_mismatch",
        "arguments_digest_mismatch",
        "order_mismatch",
        "declared_count_mismatch",
    ]
    reference_index: int | None = None
    evidence_index: int | None = None
    tool_name: str | None = None
    detail: str


class ComparisonReport(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.comparison-report/v1"] = Field(
        default=COMPARISON_REPORT_SCHEMA,
        alias="schema",
    )
    session_id: str
    ok: bool
    verdict: WitnessVerdict
    reference_action_count: int
    evidence_action_count: int
    completeness_claim: str
    findings: list[HopFinding] = Field(default_factory=list)
    note: str


class BehavioralVerdict(StrEnum):
    COMPLIANT = "COMPLIANT"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    PROHIBITED_TOOL = "PROHIBITED_TOOL"
    INVALID_TOOL_ARGS = "INVALID_TOOL_ARGS"


class BehavioralAction(BaseModel):
    index: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    verdict: str | None = None


class BehavioralScenario(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.behavioral-scenario/v1"] = Field(alias="schema")
    name: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    approval_granted: bool = False
    actions: list[BehavioralAction] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_contiguous_indices(self) -> BehavioralScenario:
        indices = [action.index for action in self.actions]
        expected = list(range(len(self.actions)))
        if sorted(indices) != expected:
            raise ValueError("behavioral action indices must be contiguous starting at 0")
        return self


class BehavioralFinding(BaseModel):
    kind: Literal[
        "prohibited_tool",
        "approval_required",
        "missing_argument",
        "invalid_argument",
        "denied_action",
    ]
    action_index: int = Field(ge=0)
    tool_name: str
    detail: str


class BehavioralReport(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.behavioral-report/v1"] = Field(
        default=BEHAVIORAL_REPORT_SCHEMA,
        alias="schema",
    )
    session_id: str
    scenario_name: str
    ok: bool
    verdict: BehavioralVerdict
    action_count: int
    approval_granted: bool
    findings: list[BehavioralFinding] = Field(default_factory=list)
    note: str


class SuiteCaseBaseline(BaseModel):
    ok: bool
    verdict: str


class SuiteBaseline(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.suite-baseline/v1"] = Field(alias="schema")
    suite: Literal["behavioral", "evidence"]
    cases: dict[str, SuiteCaseBaseline]


class SuiteRunSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: Literal["witnessdiff.suite-run/v1"] = Field(
        default="witnessdiff.suite-run/v1",
        alias="schema",
    )
    suite: Literal["behavioral", "evidence"]
    passed: int
    failed: int
    cases: dict[str, dict[str, Any]]

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    reference: dict[str, Any]
    evidence: dict[str, Any]


class ComparisonRunSummary(BaseModel):
    id: UUID
    session_id: str
    ok: bool
    verdict: str
    reference_action_count: int
    evidence_action_count: int
    completeness_claim: str
    created_at: datetime


class ComparisonRunDetail(ComparisonRunSummary):
    reference: dict[str, Any]
    evidence: dict[str, Any]
    report: dict[str, Any]


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "witnessdiff-api"
    store: str
    version: str


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    detail: str | None = None


class SuiteRunResponse(BaseModel):
    suite: str
    passed: int
    failed: int
    messages: list[str] = Field(default_factory=list)

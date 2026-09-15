from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class StoredComparisonRun:
    id: UUID
    session_id: str
    ok: bool
    verdict: str
    reference_action_count: int
    evidence_action_count: int
    completeness_claim: str
    reference_json: dict[str, Any]
    evidence_json: dict[str, Any]
    report_json: dict[str, Any]
    created_at: datetime


class RunStore(ABC):
    @abstractmethod
    def init(self) -> None: ...

    @abstractmethod
    def save_comparison(
        self,
        *,
        session_id: str,
        ok: bool,
        verdict: str,
        reference_action_count: int,
        evidence_action_count: int,
        completeness_claim: str,
        reference_json: dict[str, Any],
        evidence_json: dict[str, Any],
        report_json: dict[str, Any],
    ) -> StoredComparisonRun: ...

    @abstractmethod
    def get_comparison(self, run_id: UUID) -> StoredComparisonRun | None: ...

    @abstractmethod
    def list_comparisons(self, limit: int = 50) -> list[StoredComparisonRun]: ...


class InMemoryRunStore(RunStore):
    def __init__(self) -> None:
        self._runs: dict[UUID, StoredComparisonRun] = {}

    def init(self) -> None:
        return None

    def save_comparison(
        self,
        *,
        session_id: str,
        ok: bool,
        verdict: str,
        reference_action_count: int,
        evidence_action_count: int,
        completeness_claim: str,
        reference_json: dict[str, Any],
        evidence_json: dict[str, Any],
        report_json: dict[str, Any],
    ) -> StoredComparisonRun:
        run_id = uuid.uuid4()
        stored = StoredComparisonRun(
            id=run_id,
            session_id=session_id,
            ok=ok,
            verdict=verdict,
            reference_action_count=reference_action_count,
            evidence_action_count=evidence_action_count,
            completeness_claim=completeness_claim,
            reference_json=reference_json,
            evidence_json=evidence_json,
            report_json=report_json,
            created_at=datetime.now(tz=UTC),
        )
        self._runs[run_id] = stored
        return stored

    def get_comparison(self, run_id: UUID) -> StoredComparisonRun | None:
        return self._runs.get(run_id)

    def list_comparisons(self, limit: int = 50) -> list[StoredComparisonRun]:
        runs = sorted(self._runs.values(), key=lambda run: run.created_at, reverse=True)
        return runs[:limit]


class PostgresRunStore(RunStore):
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        import psycopg

        return psycopg.connect(self.database_url)

    def init(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS comparison_runs (
                      id UUID PRIMARY KEY,
                      session_id TEXT NOT NULL,
                      ok BOOLEAN NOT NULL,
                      verdict TEXT NOT NULL,
                      reference_action_count INT NOT NULL,
                      evidence_action_count INT NOT NULL,
                      completeness_claim TEXT NOT NULL,
                      reference_json JSONB NOT NULL,
                      evidence_json JSONB NOT NULL,
                      report_json JSONB NOT NULL,
                      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS comparison_runs_created_at_idx
                    ON comparison_runs (created_at DESC)
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS comparison_runs_session_id_idx
                    ON comparison_runs (session_id)
                    """
                )
            conn.commit()

    def save_comparison(
        self,
        *,
        session_id: str,
        ok: bool,
        verdict: str,
        reference_action_count: int,
        evidence_action_count: int,
        completeness_claim: str,
        reference_json: dict[str, Any],
        evidence_json: dict[str, Any],
        report_json: dict[str, Any],
    ) -> StoredComparisonRun:
        run_id = uuid.uuid4()
        created_at = datetime.now(tz=UTC)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO comparison_runs (
                      id, session_id, ok, verdict,
                      reference_action_count, evidence_action_count,
                      completeness_claim, reference_json, evidence_json,
                      report_json, created_at
                    ) VALUES (
                      %s, %s, %s, %s,
                      %s, %s,
                      %s, %s::jsonb, %s::jsonb,
                      %s::jsonb, %s
                    )
                    """,
                    (
                        str(run_id),
                        session_id,
                        ok,
                        verdict,
                        reference_action_count,
                        evidence_action_count,
                        completeness_claim,
                        json.dumps(reference_json),
                        json.dumps(evidence_json),
                        json.dumps(report_json),
                        created_at,
                    ),
                )
            conn.commit()
        return StoredComparisonRun(
            id=run_id,
            session_id=session_id,
            ok=ok,
            verdict=verdict,
            reference_action_count=reference_action_count,
            evidence_action_count=evidence_action_count,
            completeness_claim=completeness_claim,
            reference_json=reference_json,
            evidence_json=evidence_json,
            report_json=report_json,
            created_at=created_at,
        )

    def get_comparison(self, run_id: UUID) -> StoredComparisonRun | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, session_id, ok, verdict,
                           reference_action_count, evidence_action_count,
                           completeness_claim, reference_json, evidence_json,
                           report_json, created_at
                    FROM comparison_runs
                    WHERE id = %s
                    """,
                    (str(run_id),),
                )
                row = cur.fetchone()
        if not row:
            return None
        return _row_to_stored(row)

    def list_comparisons(self, limit: int = 50) -> list[StoredComparisonRun]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, session_id, ok, verdict,
                           reference_action_count, evidence_action_count,
                           completeness_claim, reference_json, evidence_json,
                           report_json, created_at
                    FROM comparison_runs
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [_row_to_stored(row) for row in rows]


def _row_to_stored(row: tuple) -> StoredComparisonRun:
    return StoredComparisonRun(
        id=UUID(str(row[0])),
        session_id=row[1],
        ok=row[2],
        verdict=row[3],
        reference_action_count=row[4],
        evidence_action_count=row[5],
        completeness_claim=row[6],
        reference_json=row[7] if isinstance(row[7], dict) else json.loads(row[7]),
        evidence_json=row[8] if isinstance(row[8], dict) else json.loads(row[8]),
        report_json=row[9] if isinstance(row[9], dict) else json.loads(row[9]),
        created_at=row[10],
    )


def build_run_store(database_url: str | None) -> RunStore:
    if database_url:
        return PostgresRunStore(database_url)
    return InMemoryRunStore()

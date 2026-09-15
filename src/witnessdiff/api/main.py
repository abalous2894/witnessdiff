from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from witnessdiff import __version__
from witnessdiff.api.schemas import (
    CompareRequest,
    ComparisonRunDetail,
    ComparisonRunSummary,
    ErrorResponse,
    HealthResponse,
)
from witnessdiff.api.service import (
    get_comparison_run,
    list_comparison_runs,
    run_and_persist_comparison,
    run_demo_comparison,
    run_suite,
)
from witnessdiff.api.store import PostgresRunStore, RunStore, build_run_store


def _fixtures_root() -> Path:
    override = os.environ.get("WITNESSDIFF_FIXTURES_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[3] / "fixtures"


def _database_url() -> str | None:
    return os.environ.get("DATABASE_URL") or os.environ.get("WITNESSDIFF_DATABASE_URL")


def _cors_origins() -> list[str]:
    raw = os.environ.get(
        "WITNESSDIFF_CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app(store: RunStore | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        run_store = store or build_run_store(_database_url())
        run_store.init()
        app.state.store = run_store
        app.state.store_kind = (
            "postgres" if isinstance(run_store, PostgresRunStore) else "memory"
        )
        yield

    app = FastAPI(
        title="WitnessDiff API",
        version=__version__,
        description="Persist and query witness-integrity comparison runs.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_store(request: Request) -> RunStore:
        return request.app.state.store

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        return HealthResponse(
            store=request.app.state.store_kind,
            version=__version__,
        )

    @app.post("/v1/compare", response_model=ComparisonRunDetail)
    def compare(
        body: CompareRequest,
        run_store: RunStore = Depends(get_store),
    ) -> ComparisonRunDetail:
        try:
            return run_and_persist_comparison(run_store, body.reference, body.evidence)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/v1/runs", response_model=list[ComparisonRunSummary])
    def list_runs(
        limit: int = Query(default=50, ge=1, le=200),
        run_store: RunStore = Depends(get_store),
    ) -> list[ComparisonRunSummary]:
        return list_comparison_runs(run_store, limit=limit)

    @app.get("/v1/runs/{run_id}", response_model=ComparisonRunDetail)
    def get_run(
        run_id: UUID,
        run_store: RunStore = Depends(get_store),
    ) -> ComparisonRunDetail:
        detail = get_comparison_run(run_store, run_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="comparison run not found")
        return detail

    @app.post("/v1/demo/silent-omission", response_model=ComparisonRunDetail)
    def demo_silent_omission(run_store: RunStore = Depends(get_store)) -> ComparisonRunDetail:
        return run_demo_comparison(run_store, _fixtures_root(), "silent-omission")

    @app.post("/v1/suites/{suite_name}/run")
    def run_named_suite(suite_name: str) -> Response:
        if suite_name not in {"evidence", "behavioral"}:
            raise HTTPException(status_code=404, detail="unknown suite")
        try:
            result = run_suite(_fixtures_root(), suite_name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        status = 200 if result.failed == 0 else 422
        return JSONResponse(status_code=status, content=result.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        if isinstance(exc.detail, str):
            payload = ErrorResponse(error=exc.detail)
        else:
            payload = ErrorResponse(error="request failed", detail=str(exc.detail))
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    return app


app = create_app()

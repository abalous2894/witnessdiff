"""API boundary and fail-closed security checks."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from witnessdiff.api.main import create_app
from witnessdiff.api.store import InMemoryRunStore


@pytest.fixture
def client():
    store = InMemoryRunStore()
    store.init()
    app = create_app(store=store)
    with TestClient(app) as test_client:
        yield test_client


def test_compare_rejects_unsupported_reference_schema(client: TestClient):
    response = client.post(
        "/v1/compare",
        json={
            "reference": {"schema": "evil/v1", "session_id": "x", "actions": []},
            "evidence": {
                "schema": "witnessdiff.evidence-bundle/v1",
                "session_id": "x",
                "source": "agent_platform_export",
                "completeness_claim": "unknown",
                "actions": [],
            },
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert "unsupported schema" in body.get("error", "").lower() or "unsupported schema" in str(
        body
    ).lower()
    assert "traceback" not in response.text.lower()


def test_compare_rejects_non_object_payload(client: TestClient):
    response = client.post(
        "/v1/compare",
        json={"reference": "not-an-object", "evidence": {}},
    )
    assert response.status_code == 422


def test_unknown_suite_name_returns_404(client: TestClient):
    response = client.post("/v1/suites/evil/run")
    assert response.status_code == 404
    assert response.json()["error"] == "unknown suite"


def test_suite_name_path_traversal_blocked(client: TestClient):
    response = client.post("/v1/suites/..%2Fevidence/run")
    assert response.status_code in {404, 405, 422}


def test_list_runs_limit_bounded(client: TestClient):
    over = client.get("/v1/runs?limit=9999")
    assert over.status_code == 422
    ok = client.get("/v1/runs?limit=50")
    assert ok.status_code == 200


def test_error_responses_do_not_leak_stack_traces(client: TestClient):
    response = client.post(
        "/v1/compare",
        json={
            "reference": {"schema": "not-a-real-schema/v1", "session_id": "a", "actions": []},
            "evidence": {
                "schema": "witnessdiff.evidence-bundle/v1",
                "session_id": "a",
                "source": "x",
                "completeness_claim": "unknown",
                "actions": [],
            },
        },
    )
    assert response.status_code == 400
    payload = response.text
    assert "Traceback" not in payload
    assert 'File "' not in payload


def test_session_mismatch_returns_invalid_input_verdict_not_http_500(client: TestClient):
    response = client.post(
        "/v1/compare",
        json={
            "reference": {
                "schema": "witnessdiff.reference-trace/v1",
                "session_id": "session-a",
                "source": "instrumented_mcp_runner",
                "actions": [{"index": 0, "tool_name": "crm_lookup", "action_id": "a" * 64}],
            },
            "evidence": {
                "schema": "witnessdiff.evidence-bundle/v1",
                "session_id": "session-b",
                "source": "agent_platform_export",
                "completeness_claim": "unknown",
                "actions": [{"index": 0, "tool_name": "crm_lookup", "action_id": "a" * 64}],
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["verdict"] == "INVALID_INPUT"


def test_compare_accepts_large_but_bounded_action_list(client: TestClient):
    actions = [
        {"index": i, "tool_name": "crm_lookup", "action_id": f"{i:064x}"} for i in range(200)
    ]
    reference = {
        "schema": "witnessdiff.reference-trace/v1",
        "session_id": "bulk",
        "source": "instrumented_mcp_runner",
        "actions": actions,
    }
    evidence = {
        "schema": "witnessdiff.evidence-bundle/v1",
        "session_id": "bulk",
        "source": "agent_platform_export",
        "completeness_claim": "complete_path",
        "actions": actions,
    }
    response = client.post(
        "/v1/compare",
        json={"reference": reference, "evidence": evidence},
    )
    assert response.status_code == 200
    assert response.json()["verdict"] == "COMPLETE"
    assert len(json.dumps(response.json())) > 1000

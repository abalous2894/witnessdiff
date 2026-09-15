import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from witnessdiff.api.main import create_app
from witnessdiff.api.store import InMemoryRunStore

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "evidence"


@pytest.fixture
def client():
    store = InMemoryRunStore()
    store.init()
    app = create_app(store=store)
    with TestClient(app) as test_client:
        yield test_client


def _load(name: str) -> tuple[dict, dict]:
    reference = json.loads((FIXTURES / f"{name}.reference.json").read_text(encoding="utf-8"))
    evidence = json.loads((FIXTURES / f"{name}.evidence.json").read_text(encoding="utf-8"))
    return reference, evidence


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["store"] == "memory"


def test_compare_persists_run(client: TestClient):
    reference, evidence = _load("silent-omission")
    response = client.post("/v1/compare", json={"reference": reference, "evidence": evidence})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["verdict"] == "COMPLETENESS_OVERCLAIM"
    assert body["session_id"] == "demo-refund-001"
    run_id = body["id"]

    detail = client.get(f"/v1/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["report"]["verdict"] == "COMPLETENESS_OVERCLAIM"

    listing = client.get("/v1/runs")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_compare_complete_path(client: TestClient):
    reference, evidence = _load("complete-path")
    response = client.post("/v1/compare", json={"reference": reference, "evidence": evidence})
    assert response.status_code == 200
    assert response.json()["verdict"] == "COMPLETE"


def test_get_missing_run(client: TestClient):
    response = client.get("/v1/runs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_run_evidence_suite(client: TestClient):
    response = client.post("/v1/suites/evidence/run")
    assert response.status_code == 200
    body = response.json()
    assert body["suite"] == "evidence"
    assert body["failed"] == 0
    assert body["passed"] == 10


def test_run_behavioral_suite(client: TestClient):
    response = client.post("/v1/suites/behavioral/run")
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] == 5


def test_demo_silent_omission(client: TestClient):
    response = client.post("/v1/demo/silent-omission")
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "COMPLETENESS_OVERCLAIM"
    assert body["reference_action_count"] == 4
    assert body["evidence_action_count"] == 3

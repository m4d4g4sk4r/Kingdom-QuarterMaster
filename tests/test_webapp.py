import pytest
from fastapi.testclient import TestClient

from kqm.webapp import create_app


@pytest.fixture
def client():
    return TestClient(create_app(mock=True))


def test_root_reports_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_snapshot_endpoint_returns_reconciled_agents(client):
    resp = client.get("/api/snapshot")
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == 4700
    names = {a["agent_name"] for a in body["agents"]}
    assert names == {"Gekko", "Fade"}


def test_recommend_endpoint_returns_a_plan(client):
    resp = client.get("/api/recommend")
    assert resp.status_code == 200
    body = resp.json()
    assert body["balance"] == 4700
    assert "purchases" in body["plan"]


def test_recommend_endpoint_applies_weight_override(client):
    resp = client.get("/api/recommend", params={"weight": "buddy=10"})
    assert resp.status_code == 200
    assert "purchases" in resp.json()["plan"]


def test_goal_endpoint_returns_plan_for_known_agent(client):
    resp = client.get("/api/goal/Gekko")
    assert resp.status_code == 200
    body = resp.json()
    assert body["plan"]["agent_name"] == "Gekko"


def test_goal_endpoint_404s_for_unknown_agent(client):
    resp = client.get("/api/goal/NotAnAgent")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "agent_not_found"

import importlib

from fastapi.testclient import TestClient

import api.server as server
from core.reliability import ResilienceError


def test_invoke_agent_success(monkeypatch):
    importlib.reload(server)

    class FakeAgent:
        def run(self, query, environment):
            return {"output": f"Echo: {query}"}

    monkeypatch.setattr(server, "get_agent_instance", lambda: FakeAgent())
    monkeypatch.setattr(server, "sensor_reader", lambda _: [{"device_id": "temp_sensor_01", "status": "ok"}])

    with TestClient(server.app) as client:
        response = client.post(
            "/api/v1/agent/invoke",
            json={"query": "当前状态如何？"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["output"].startswith("Echo")


def test_invoke_agent_environment_failure(monkeypatch):
    importlib.reload(server)

    class FakeAgent:
        def run(self, query, environment):
            return {"output": "ok"}

    monkeypatch.setattr(server, "get_agent_instance", lambda: FakeAgent())
    monkeypatch.setattr(server, "sensor_reader", lambda _: [{"error": "hardware offline"}])

    with TestClient(server.app) as client:
        response = client.post(
            "/api/v1/agent/invoke",
            json={"query": "检查设备"},
        )

    assert response.status_code == 503


def test_invoke_agent_resilience_failure(monkeypatch):
    importlib.reload(server)

    class FailingAgent:
        def run(self, query, environment):
            raise ResilienceError("agent", 2, RuntimeError("timeout"))

    monkeypatch.setattr(server, "get_agent_instance", lambda: FailingAgent())
    monkeypatch.setattr(server, "sensor_reader", lambda _: [{"device_id": "temp", "status": "ok"}])

    with TestClient(server.app) as client:
        response = client.post(
            "/api/v1/agent/invoke",
            json={"query": "执行任务"},
        )

    assert response.status_code == 503

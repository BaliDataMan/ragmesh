"""API layer against a stub agent — no real LLM/MCP wiring exercised here."""

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from ragmesh.api import app, get_agent


class _StubAgent:
    async def ainvoke(self, inputs: dict) -> dict:
        return {"messages": [*inputs["messages"], AIMessage(content="stub answer")]}


app.dependency_overrides[get_agent] = lambda: _StubAgent()
client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_answer() -> None:
    response = client.post("/chat", json={"question": "What is ragmesh?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "stub answer"}

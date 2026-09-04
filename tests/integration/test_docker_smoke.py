"""End-to-end smoke test: real `docker compose up` + a live HTTP call.

Opt-in tier — needs Docker and a real LLM API key in `.env`. Not run by CI by
default (see project-docs/architecture-rationale.md #11); run manually before tagging
a release: `uv run pytest tests/integration -m slow`.
"""

import subprocess
import time

import httpx
import pytest

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def compose_stack():
    subprocess.run(["docker", "compose", "up", "--build", "-d"], check=True)
    try:
        for _ in range(60):
            try:
                if httpx.get("http://localhost:8080/health", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(2)
        else:
            raise TimeoutError("agent-api did not become healthy in time")
        yield
    finally:
        subprocess.run(["docker", "compose", "down"], check=True)


def test_chat_endpoint_answers_grounded_question(compose_stack: None) -> None:
    response = httpx.post(
        "http://localhost:8080/chat",
        json={"question": "What MCP transport does ragmesh use?"},
        timeout=60,
    )

    assert response.status_code == 200
    assert "streamable" in response.json()["answer"].lower()

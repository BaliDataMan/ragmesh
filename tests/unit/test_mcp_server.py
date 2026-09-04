"""Proves the MCP server's tool contract via an in-memory session — no network/Docker."""

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from ragmesh.mcp_server.server import mcp


@pytest.fixture(autouse=True)
def _fake_search(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ragmesh.mcp_server.server.search_documents",
        lambda query, k=4: [{"source": "README.md", "content": f"stub result for {query!r}"}],
    )


@pytest.mark.asyncio
async def test_search_documents_tool_is_registered() -> None:
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        tools = await client.list_tools()

    tool_names = {tool.name for tool in tools.tools}
    assert "search_documents_tool" in tool_names


@pytest.mark.asyncio
async def test_search_documents_tool_call_returns_result() -> None:
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        result = await client.call_tool("search_documents_tool", {"query": "MCP transport"})

    assert not result.isError

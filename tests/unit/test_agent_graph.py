"""Agent graph wiring, decoupled from MCP transport: a fake model + a plain @tool stand-in."""

from typing import Any

import pytest
from langchain.agents import create_agent
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool


@tool
def fake_search(query: str) -> str:
    """Search stand-in for the real MCP search_documents_tool."""
    return f"stub result for {query!r}"


class _ScriptedToolCallingModel(GenericFakeChatModel):
    """GenericFakeChatModel doesn't implement bind_tools; create_agent requires it."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> Runnable:
        return self


def _scripted_model() -> _ScriptedToolCallingModel:
    messages = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "fake_search", "args": {"query": "MCP transport"}, "id": "call_1"}
                ],
            ),
            AIMessage(content="ragmesh uses streamable-http, per the ADR."),
        ]
    )
    return _ScriptedToolCallingModel(messages=messages)


@pytest.mark.asyncio
async def test_agent_calls_tool_then_answers() -> None:
    agent = create_agent(_scripted_model(), tools=[fake_search])

    question = HumanMessage(content="What transport does ragmesh use?")
    result = await agent.ainvoke({"messages": [question]})

    final = result["messages"][-1]
    assert "streamable-http" in final.content
    tool_messages = [m for m in result["messages"] if getattr(m, "name", None) == "fake_search"]
    assert len(tool_messages) == 1
    assert "MCP transport" in tool_messages[0].content

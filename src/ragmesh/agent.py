"""Wires the MCP retrieval tool into a ReAct-style agent, built once and cached.

Uses `langchain.agents.create_agent` — the current, LangGraph-backed agent factory
that superseded `langgraph.prebuilt.create_react_agent` (deprecated upstream).
"""

from typing import Any

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from ragmesh.config import settings
from ragmesh.llm import get_chat_model

SYSTEM_PROMPT = (
    "You are ragmesh's own documentation assistant. Use the search_documents_tool "
    "to find relevant passages before answering questions about ragmesh's architecture. "
    "Cite the source file(s) you drew from."
)


async def build_agent() -> Any:
    client = MultiServerMCPClient(
        {
            "ragmesh-retrieval": {
                "url": settings.mcp_server_url,
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    return create_agent(get_chat_model(), tools=tools, system_prompt=SYSTEM_PROMPT)

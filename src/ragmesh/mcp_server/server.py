"""The retrieval tool as a real MCP server, over streamable-http (see
project-docs/adr/0001).

Run as `python -m ragmesh.mcp_server.server`, or via the mcp-server Docker service.
"""

from mcp.server.fastmcp import FastMCP

from ragmesh.retrieval import search_documents

mcp = FastMCP("ragmesh-retrieval", host="0.0.0.0", port=8000)


@mcp.tool()
def search_documents_tool(query: str, k: int = 4) -> list[dict[str, str]]:
    """Search ragmesh's own documentation (README + ADRs) for passages relevant to `query`."""
    return search_documents(query, k=k)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

# ADR-0002: MCP server built on the official `mcp` SDK's FastMCP, not `jlowin/fastmcp`

## Status
Accepted

## Context
Two `FastMCP` implementations exist: `mcp.server.fastmcp.FastMCP`, shipped in
the official Anthropic-maintained `mcp` Python SDK, and the standalone
third-party `fastmcp` package (PrefectHQ/jlowin), which has broader ergonomics
and a convenient in-memory test `Client`.

## Decision
Use the official SDK's `FastMCP`.

## Rationale
This repo exists to demonstrate correct use of the MCP ecosystem, and "used
the standard, spec-reference implementation correctly" is a better signal for
that purpose than "found a nicer third-party wrapper." It also keeps this
codebase's testing approach aligned with `langchain-mcp-adapters`, whose own
reference examples are built against the official SDK — so the two libraries'
idioms match instead of fighting each other.

## Consequences
Possibly more boilerplate than `jlowin/fastmcp` would require. Accepted: the
signal matters more than the convenience for a portfolio repo.

## Revisit when
If the official SDK's public API churns badly across a major version — verify
the `FastMCP` class name and constructor shape against whatever version is
pinned before writing code against a new release.

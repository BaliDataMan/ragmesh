# ADR-0001: MCP transport is streamable-http, not stdio or SSE

## Status
Accepted

## Context
The retrieval tool is served by a real MCP server running in its own container
(see the mesh architecture this repo is named for), separate from the agent
process. MCP supports three transports: stdio, SSE, and streamable-http.

## Decision
Use streamable-http.

## Rationale
- **stdio** requires client and server to share a process tree (pipes over
  stdin/stdout). It cannot cross the Docker network boundary between the
  `agent-api` and `mcp-server` containers, so it's not an option here — not a
  judgment call, a hard constraint.
- **SSE** is the older two-endpoint HTTP transport from MCP's original spec.
  The 2025-03-26 spec revision superseded it with streamable-http, a single
  endpoint that supports both request/response and streaming.
- **streamable-http** is the current spec-recommended network transport.
  Shipping SSE in new code reads as not having kept up with the protocol.

## Consequences
The MCP server needs an actual HTTP listener, a port, and a health check —
more moving parts than stdio, but this is the same cost SSE would have
incurred anyway, so it isn't a trade-off against SSE, only against the
infeasible stdio option.

## Revisit when
The MCP spec changes transports again — check before assuming this still holds.

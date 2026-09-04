# ADR-0003: Local embeddings + FAISS, not a managed vector DB or paid embeddings API

## Status
Accepted

## Context
Retrieval needs an embedding model and a vector index. Options range from a
fully managed vector database (Pinecone, Weaviate) with a paid embeddings API,
to a fully local stack running on-disk.

## Decision
Use local, no-API-key embeddings (`sentence-transformers/all-MiniLM-L6-v2` via
`langchain-huggingface`) indexed into a local FAISS store
(`langchain_community.vectorstores.FAISS`).

## Rationale
`docker compose up` should require exactly one secret — the chat LLM's API
key — not two. A second required key (for a paid embeddings API) or a managed
vector DB account raises the barrier for anyone, including an interviewer,
trying to actually run the repo. FAISS is also the right scale for a small,
static sample corpus (this repo's own docs); a managed vector DB would be
over-engineering here.

## Consequences
- FAISS-on-local-disk is not how retrieval would be done at production scale.
  This is a deliberate, documented simplification, not an oversight.
- Retrieval quality from a small local embedding model is weaker than
  commercial embeddings would give.
- The index is built at Docker image build time (`RUN python -m ragmesh.ingest`
  after copying the source docs), not at container startup — deterministic,
  fast cold starts, no race between the agent querying the MCP server and the
  index finishing its build. The cost: editing `project-docs/adr/` or `README.md`
  requires `docker compose up --build`, not just a restart, to take effect.

## Revisit when
A later milestone wants to demonstrate a "swap the vector store via config"
story analogous to the LLM provider swap — reasonable v0.2+ scope, not v0.1.

# ragmesh v0.1 — Architecture Rationale & Trade-offs

This document is the "why" companion to the v0.1 implementation plan. It exists so that anyone reading the code later — including future-you — can reconstruct the reasoning behind each structural choice without having to re-derive it, and can tell a deliberate decision from an accident.

It's broader and more narrative than the formal `project-docs/adr/000X-*.md` records planned for a few of these topics (transport, MCP server library, embeddings). Treat those ADRs as the short canonical record of a single decision each; treat this file as the fuller map of how all the decisions fit together, including ones too small to deserve their own ADR.

Each entry follows the same shape: **Decision → Why → Alternatives rejected → Trade-off accepted → Revisit when**. That last field matters as much as the decision itself — it's what keeps a decision from calcifying into dogma.

---

## 1. Scope: full v0.1, not the minimal 80/20 version

**Decision:** Build the complete v0.1 milestone — real MCP server over the network, FAISS retrieval, Docker Compose, tests, CI — rather than the minimal "one agent + one MCP server + README + 2 ADRs, then stop" version.

**Why:** Two internal planning docs disagreed on scope. The minimal version optimizes for time-to-pin (2 weekends) on the theory that a README + Mermaid diagram + ADRs carry most of the "architect signal" a recruiter needs. The full version costs more time but produces something a technical interviewer can actually run, poke at, and ask follow-up questions about — which matters more once you're past the resume-screen stage and into a technical conversation.

**Alternatives rejected:** Minimal 2-ADR version (faster, but there's nothing to demo beyond static docs — a skeptical interviewer's "can I see it work?" has no answer).

**Trade-off accepted:** More build time and more surface area to maintain/abandon. This is the single biggest risk to this plan — see the scope-creep warning in the source planning docs themselves (the Substack pattern: two strong bursts, then silence).

**Revisit when:** If time pressure mounts (interviews imminent) or the build stalls past ~2 weekends of actual effort, fall back to shipping whatever subset is runnable and pin that — a working v0.1-minus-Docker beats an unshipped v0.1-full.

---

## 2. Agent framework: LangGraph `create_react_agent`

**Decision:** Use LangGraph's prebuilt ReAct agent rather than a hand-rolled agent loop or a different framework (CrewAI, AutoGen).

**Why:** The resume claim is specifically LangGraph. Using the prebuilt `create_react_agent` rather than hand-rolling the reasoning loop is itself a small signal of ecosystem fluency — a portfolio repo that reinvents a solved primitive reads as not knowing the primitive exists.

**Alternatives rejected:** Custom agent loop (more "from scratch" cred, but reinvents something LangGraph already does well, and is worse ROI for the time budget); CrewAI/AutoGen (don't match the specific resume claim).

**Trade-off accepted:** Coupling to LangGraph's abstractions and release cadence. Acceptable — that coupling *is* the point of the repo.

**Revisit when:** v0.2 introduces a supervisor routing to multiple agents — at that point `create_react_agent` becomes one node among several in a larger graph, not a replacement decision.

---

## 3. Tool delivery: a real MCP server over the network, not in-process tools

**Decision:** The retrieval tool lives behind an actual MCP server process, reachable over the network (Docker service), rather than being a plain Python function decorated as a LangChain tool in the same process as the agent.

**Why:** This is the entire thesis of "ragmesh" (retrieval *as a mesh of MCP services*). If the retrieval tool were just an in-process function, the repo would demonstrate LangGraph and RAG, but not MCP — and MCP is one of the three named resume claims this repo exists to back up.

**Alternatives rejected:** In-process tool function (simpler, no transport/Docker complexity, but doesn't prove MCP skill at all — a reviewer who reads the code would see a decorator, not a protocol).

**Trade-off accepted:** Real distributed-systems complexity for a "hello world"-scale retrieval task — network transport, container orchestration, health checks, a whole class of failure modes (server not ready, connection refused) that a single-process app wouldn't have. This complexity is deliberately not hidden; it's the demonstrated skill.

**Revisit when:** Never, for this repo's purpose — this is the load-bearing architectural choice, not incidental complexity.

---

## 4. MCP transport: streamable-http, not stdio or SSE

**Decision:** The MCP server communicates over the streamable-http transport.

**Why:** stdio (the simplest MCP transport) only works when client and server share a process tree — it cannot cross a Docker network boundary, which this architecture requires (see #3). Between the two network-capable options, SSE is the older two-endpoint transport that the MCP spec's 2025-03-26 revision superseded; streamable-http is the current single-endpoint transport. Shipping SSE in a 2026 portfolio repo reads as not having kept up with the spec.

**Alternatives rejected:** stdio (ruled out by the container boundary, not a judgment call); SSE (works, but signals staleness).

**Trade-off accepted:** Streamable-http is slightly more moving parts than stdio (an actual HTTP server, a port, a health check) — but this cost is identical to what SSE would have cost anyway, so it's not really a trade-off against SSE, just against the (infeasible) stdio option.

**Revisit when:** The MCP spec changes again — check this before writing the code, since transport recommendations in this space have moved before and may move again.

---

## 5. MCP server library: official `mcp` SDK's `FastMCP`, not `jlowin/fastmcp`

**Decision:** Build the server with `from mcp.server.fastmcp import FastMCP` (the Anthropic-maintained reference SDK), not the standalone third-party `fastmcp` package (PrefectHQ/jlowin), despite the latter having arguably nicer developer ergonomics.

**Why:** For a repo whose job is to prove "I know this ecosystem correctly," using the boring, official, spec-reference implementation is a better signal than using a fancier wrapper — "I used the standard tool correctly" beats "I found a nicer third-party tool." It also keeps the codebase's testing story aligned with `langchain-mcp-adapters`' own reference examples, which are built against the official SDK.

**Alternatives rejected:** `jlowin/fastmcp` (genuinely nicer DX and a good in-memory test `Client`, but it's a judgment call between "official-SDK signal" and "better ergonomics" — worth its own short ADR precisely because it's close).

**Trade-off accepted:** Possibly more boilerplate than the third-party alternative; accepted because the signal matters more than the convenience here.

**Revisit when:** If the official SDK's API churns badly (there were unconfirmed rumors of a `FastMCP`→`MCPServer` rename in a v2.0 beta at time of writing — verify the actual class name against whatever version gets pinned before writing code).

---

## 6. LLM provider abstraction: `init_chat_model`, not a hand-rolled factory

**Decision:** All chat-model construction goes through LangChain's `init_chat_model(model, model_provider=...)`, driven by a `pydantic-settings` config reading `RAGMESH_LLM_PROVIDER`/`RAGMESH_LLM_MODEL` from the environment. Anthropic is the default provider for the running demo; OpenAI and Bedrock (`bedrock_converse`) are supported as optional-dependency extras.

**Why:** The playbook's engineering checklist calls out "config, not hardcoding — pluggability is an architecture demonstration in itself." `init_chat_model` already does exactly this, correctly, with no custom code. Writing a bespoke provider-factory class here would be effort spent re-solving a solved problem — the kind of unnecessary abstraction that looks like busywork rather than judgment.

**Alternatives rejected:** Hand-rolled `if provider == "anthropic": ... elif ...` factory (more "look what I built," but it's reinventing a library function, which is a worse signal, not a better one).

**Trade-off accepted:** Provider coverage is bounded by whatever `init_chat_model` supports upstream. Acceptable — the three providers on the resume (OpenAI/Anthropic/Bedrock) are all supported.

**Revisit when:** A provider not covered by `init_chat_model` needs supporting.

---

## 7. Retrieval stack: local embeddings + FAISS, not a managed vector DB

**Decision:** Embeddings are local and free (`sentence-transformers/all-MiniLM-L6-v2` via `langchain-huggingface`), indexed into a local FAISS store — not a managed vector database (Pinecone, Weaviate, etc.) and not a paid embeddings API (OpenAI embeddings).

**Why:** `docker compose up` should require exactly one secret (the chat LLM's API key), not two. Anyone cloning the repo to try it — including an interviewer — hits a lower barrier to actually running it. FAISS is also genuinely the right scale for a "sample document set" demo; a managed vector DB would be over-engineering for the data volume involved.

**Alternatives rejected:** OpenAI embeddings (better retrieval quality arguably, but forces a second required secret for zero demo-relevant benefit); managed vector DB (real production pattern, but wrong scale for v0.1 and adds an external dependency/account requirement to the quickstart).

**Trade-off accepted:** FAISS-on-local-disk is explicitly not how you'd retrieve at production scale — this is a deliberate, documented simplification (see ADR-0003), not an oversight. Retrieval quality from a small local embedding model is also weaker than commercial embeddings.

**Revisit when:** If a later milestone wants to demonstrate a "swap the vector store via config" story the same way the LLM provider is swappable — that's a reasonable v0.2+ enhancement, not v0.1 scope.

---

## 8. Sample corpus: the repo's own docs, not an external dataset

**Decision:** The document set the agent retrieves over is `project-docs/adr/*.md` + `README.md` — ragmesh answering questions about its own architecture.

**Why:** Zero external content-sourcing effort, and it's a fitting demo: "ask the RAG system how its own retrieval pipeline works" is a memorable, slightly clever way to show it off in a demo GIF or interview, and it means the corpus updates automatically as the real documentation grows.

**Alternatives rejected:** A generic external corpus (Wikipedia snippets, a public dataset) — more "realistic" feeling but requires sourcing/licensing thought for zero added signal.

**Trade-off accepted:** A self-referential demo is a little less impressive than a domain-specific one (e.g., "RAG over financial filings") would be for showing domain applicability — it demonstrates the mechanism, not a business use case. Fine for v0.1; worth reconsidering if a later milestone wants to show domain versatility.

**Revisit when:** If an interview or use-case wants to show retrieval over a "real" domain corpus — swapping the corpus is just changing what `ingest.py` points at, since retrieval logic is corpus-agnostic.

---

## 9. FAISS index build time: Docker image build, not container startup

**Decision:** The FAISS index is built once during `docker build` (`RUN python -m ragmesh.ingest` after `COPY docs/ README.md`), baked into the `mcp-server` image — not built fresh every time the container starts.

**Why:** Deterministic, fast cold starts, and no race condition where the agent queries the MCP server before the index finishes building. "It just works" on `docker compose up` matters more for a demo repo than incremental rebuild speed.

**Alternatives rejected:** Build-on-startup (avoids a rebuild-on-doc-change requirement, but introduces exactly the startup race this design avoids, and slows every `docker compose up`, not just ones after doc changes).

**Trade-off accepted:** Any change to the sample docs (`project-docs/adr/`, `README.md`) requires an image rebuild (`docker compose up --build`) to take effect, not just a container restart. This is a real annoyance during active development of the docs themselves — worth remembering so it doesn't look like a bug when a README edit doesn't show up in a plain restart.

**Revisit when:** If the corpus becomes large enough that build-time indexing meaningfully slows the Docker build — not expected at this scale.

---

## 10. Serving layer: FastAPI + CLI, deliberately no frontend

**Decision:** Expose the agent via a FastAPI `POST /chat` endpoint and a thin CLI. No web UI.

**Why:** The playbook is explicit that this repo's audience — technical reviewers and interviewers — doesn't need a UI to evaluate it; a `curl` command or CLI invocation is sufficient proof, and time spent on frontend polish is time not spent on the parts that actually carry "architect" signal (ADRs, tests, CI, the mesh architecture itself).

**Alternatives rejected:** A minimal web UI (more demo-friendly for non-technical viewers, e.g. a recruiter, but wrong effort allocation for the target audience and explicitly called out as a trap in the source playbook).

**Trade-off accepted:** Less immediately impressive to skim for a non-technical viewer glancing at a demo GIF. Mitigate this in the README with a clear `curl`/CLI example and, if wanted later, an asciinema/GIF of a terminal session rather than a built UI.

**Revisit when:** Essentially never for this repo's stated audience — if that audience changes (e.g., this becomes a real product rather than a portfolio piece), reopen the question.

---

## 11. Testing strategy: hermetic fakes for unit tests, one opt-in integration tier

**Decision:** Unit tests use `DeterministicFakeEmbedding`, `GenericFakeChatModel`, and an in-memory MCP client/server session — no real model downloads, no real network calls, no LLM API key needed to run `pytest tests/unit`. A separate, slower `tests/integration/test_docker_smoke.py` actually runs `docker compose` and hits the API; this tier is not run in CI by default since it needs a live LLM key.

**Why:** CI needs to be fast, deterministic, and runnable by anyone (including CI itself) without secrets or flaky external dependencies — that's what makes tests/CI meaningful "architect signal" rather than decoration. But hermetic tests alone can't catch real transport/Docker/networking bugs, hence keeping one true end-to-end smoke test as a separate, explicitly-labeled tier rather than pretending unit tests cover everything.

**Alternatives rejected:** Testing only against real services (slow, flaky in CI, requires secrets in CI — a non-starter for a public repo where forks/PRs shouldn't need your API key to get a green check); testing only with fakes and no integration tier at all (faster, but leaves the actual Docker/MCP wiring — the whole point of the repo — completely unverified by any test).

**Trade-off accepted:** The integration tier needs to be run manually (or via a separately-gated CI job with a repo secret) rather than on every PR — meaning a change could pass CI while still breaking the real Docker Compose wiring. Mitigate by actually running it locally before tagging a release.

**Revisit when:** If this repo gets external contributors, consider a manually-triggered CI workflow for the integration tier gated on a maintainer-approved run (avoids exposing secrets to arbitrary fork PRs).

---

## 12. Packaging: `uv` + per-provider optional-dependency groups

**Decision:** `pyproject.toml` defines `[project.optional-dependencies]` groups (`anthropic`, `openai`, `bedrock`, `all`) so installing, say, `boto3` (heavy, AWS-specific) isn't forced on someone who only wants the Anthropic path.

**Why:** Mirrors the config-driven provider swap (#6) at the packaging level — someone reading `pyproject.toml` sees the pluggability story before reading a line of code. Also keeps the default install lighter.

**Alternatives rejected:** One flat dependency list with all three provider SDKs always installed (simpler `pyproject.toml`, but forces unnecessary heavy/unused dependencies — a mild anti-signal for a repo whose whole point is demonstrating good engineering judgment).

**Trade-off accepted:** Slightly more `pyproject.toml` complexity, and the Docker image needs to explicitly pick which extras to install (currently: `anthropic` + `openai`, so the demo works out of the box with either key without pulling in `boto3`).

**Revisit when:** N/A — this is a low-regret choice.

---

## 13. Explicitly deferred beyond v0.1 (and why)

Multi-agent supervision (v0.2), eval-gated CI with a golden-question regression gate (v0.3), and one-command AWS deploy via Terraform/CDK (v1.0) are all out of scope for this pass, even though they're part of the longer-term playbook.

**Why defer:** The single biggest risk called out in the source planning docs is scoping too big and abandoning it before anything ships — the same pattern the user's own Substack has shown twice. Landing a working, tested, documented v0.1 and pinning it is worth more than an ambitious-but-unfinished v0.3. Each later milestone can be scoped and planned fresh once v0.1 is actually running, rather than speculatively designed now against assumptions that may not hold once real code exists.

**Revisit when:** v0.1 is shipped, tagged, and pinned. Not before.

---

## See also

- `docs/project-plans/v0.1-implementation-plan.md` — the concrete build plan this document explains the reasoning behind (private, gitignored).
- `docs/project-plans/Flagship-repo-Playbook.md` — the full multi-milestone plan this v0.1 is the first slice of (private, gitignored).
- `project-docs/adr/0001-mcp-transport-streamable-http.md`, `0002-fastmcp-official-sdk-vs-jlowin.md`, `0003-local-embeddings-faiss-vs-managed-vector-db.md` — the short, formal, single-topic records for the three closest judgment calls above (§4, §5, §7), to be written during the build.

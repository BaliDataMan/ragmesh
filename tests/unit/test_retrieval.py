"""Retrieval logic against a tiny in-memory FAISS index — no real model download."""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding


def _build_fake_index() -> FAISS:
    embeddings = DeterministicFakeEmbedding(size=16)
    documents = [
        Document(
            page_content="ragmesh uses streamable-http for MCP transport.",
            metadata={"source": "project-docs/adr/0001.md"},
        ),
        Document(
            page_content="ragmesh uses local FAISS for retrieval.",
            metadata={"source": "project-docs/adr/0003.md"},
        ),
    ]
    return FAISS.from_documents(documents, embeddings)


def test_similarity_search_returns_documents_with_source_metadata() -> None:
    index = _build_fake_index()

    results = index.similarity_search("MCP transport", k=1)

    assert len(results) == 1
    assert "source" in results[0].metadata


def test_similarity_search_respects_k() -> None:
    index = _build_fake_index()

    results = index.similarity_search("ragmesh", k=2)

    assert len(results) == 2

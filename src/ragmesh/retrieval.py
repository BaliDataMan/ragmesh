"""Load the pre-built FAISS index and run similarity search — used by the MCP tool."""

from functools import lru_cache

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from ragmesh.config import settings


@lru_cache(maxsize=1)
def _load_index() -> FAISS:
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    return FAISS.load_local(
        str(settings.faiss_index_dir), embeddings, allow_dangerous_deserialization=True
    )


def search_documents(query: str, k: int = settings.retrieval_k) -> list[dict[str, str]]:
    index = _load_index()
    results = index.similarity_search(query, k=k)
    return [
        {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content}
        for doc in results
    ]

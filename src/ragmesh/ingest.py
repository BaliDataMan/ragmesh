"""Build the FAISS index over ragmesh's own docs (README + ADRs) — the sample corpus.

Run as `python -m ragmesh.ingest`. Baked into the mcp-server image at Docker build
time (see project-docs/architecture-rationale.md #9) — rerun after editing the
source docs.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ragmesh.config import settings

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATHS = [
    REPO_ROOT / "README.md",
    *sorted((REPO_ROOT / "project-docs" / "adr").glob("*.md")),
]


def load_corpus() -> list[Document]:
    documents = []
    for path in CORPUS_PATHS:
        if not path.exists():
            continue
        documents.append(
            Document(
                page_content=path.read_text(),
                metadata={"source": str(path.relative_to(REPO_ROOT))},
            )
        )
    return documents


def build_index() -> None:
    documents = load_corpus()
    if not documents:
        raise RuntimeError(f"No corpus documents found under {REPO_ROOT}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    index = FAISS.from_documents(chunks, embeddings)

    settings.faiss_index_dir.mkdir(parents=True, exist_ok=True)
    index.save_local(str(settings.faiss_index_dir))
    print(
        f"Indexed {len(chunks)} chunks from {len(documents)} documents "
        f"-> {settings.faiss_index_dir}"
    )


if __name__ == "__main__":
    build_index()

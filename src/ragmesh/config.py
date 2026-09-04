"""Environment-driven settings — single source of truth for provider/model/paths."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAGMESH_", env_file=".env", extra="ignore")

    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-5-20250929"

    mcp_server_url: str = "http://localhost:8000/mcp"

    faiss_index_dir: Path = Path("data/faiss_index")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_k: int = 4


settings = Settings()

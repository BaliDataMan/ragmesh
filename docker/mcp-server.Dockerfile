FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev

COPY project-docs/ project-docs/

RUN uv run --no-dev python -m ragmesh.ingest

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "python", "-m", "ragmesh.mcp_server.server"]

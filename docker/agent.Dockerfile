FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev --extra anthropic --extra openai

EXPOSE 8080

CMD ["uv", "run", "--no-dev", "uvicorn", "ragmesh.api:app", "--host", "0.0.0.0", "--port", "8080"]

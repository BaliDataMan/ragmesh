"""FastAPI app — builds the agent once at startup (lifespan), exposes POST /chat."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from ragmesh.agent import build_agent


class AppState:
    agent: Any = None


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state.agent = await build_agent()
    yield


app = FastAPI(title="ragmesh", lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


def get_agent() -> Any:
    return state.agent


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, agent: Any = Depends(get_agent)) -> ChatResponse:  # noqa: B008
    result = await agent.ainvoke({"messages": [HumanMessage(content=request.question)]})
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

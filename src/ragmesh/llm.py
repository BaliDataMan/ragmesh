"""Single call site for chat-model construction — swap providers via config, not code."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from ragmesh.config import settings


def get_chat_model() -> BaseChatModel:
    return init_chat_model(settings.llm_model, model_provider=settings.llm_provider)

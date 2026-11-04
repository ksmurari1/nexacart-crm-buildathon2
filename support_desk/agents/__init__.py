"""AutoGen agent factory registry for the NexaCart Support Desk.

    1. query_agent       -> understands the complaint (category, urgency, sentiment, risk)
    2. knowledge_agent   -> retrieves only the relevant policy / FAQ passages (tool: search_knowledge_base)
    3. resolution_agent  -> writes a grounded, polite reply + self-rated confidence
    4. qa_agent          -> audits grounding and citations\n    5. log_agent         -> applies escalation and records ticket (tool: record_ticket)
"""
from __future__ import annotations

import logging
import warnings

from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..config import Settings
from .knowledge_agent import create_knowledge_agent
from .log_agent import create_log_agent
from .query_agent import create_query_agent
from .resolution_agent import create_resolution_agent
from .qa_agent import create_qa_agent

GENERIC_MODEL_INFO = ModelInfo(
    vision=False, function_calling=True, json_output=True, family="unknown", structured_output=False
)
# Dated model snapshots (e.g. gpt-4o-mini-2024-07-18) trigger a harmless token-estimation warning.
warnings.filterwarnings("ignore", message="Resolved model mismatch")
logging.getLogger("autogen_core.events").setLevel(logging.WARNING)  # full LLM payloads are too noisy


def create_model_client(settings: Settings) -> OpenAIChatCompletionClient:
    """OpenAI by default. Any OpenAI-compatible endpoint (Azure proxy, Groq, Ollama, LM Studio)
    works by setting OPENAI_BASE_URL + OPENAI_MODEL in .env."""
    kwargs = {"model": settings.model, "api_key": settings.api_key, "temperature": 0.1}
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    try:
        return OpenAIChatCompletionClient(**kwargs)
    except ValueError:  # unknown model name on a custom endpoint -> describe its capabilities
        return OpenAIChatCompletionClient(**kwargs, model_info=GENERIC_MODEL_INFO)


__all__ = [
    "create_model_client",
    "create_query_agent",
    "create_knowledge_agent",
    "create_resolution_agent",
    "create_qa_agent",
    "create_log_agent",
]

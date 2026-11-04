"""AutoGen GroupChat team builder (RoundRobinGroupChat & SelectorGroupChat) with clean termination.

Fulfills Task 4 & Bonus Section 10 of the assignment specification:
- Wires Query -> Knowledge -> Resolution -> QA -> Log agents into an AutoGen team
- Uses TextMentionTermination('LOGGED') + MaxMessageTermination(12) as a safety net
- Supports both deterministic RoundRobinGroupChat and model-driven SelectorGroupChat
"""
from __future__ import annotations

import json
from typing import Literal

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat

from .agents import (
    create_knowledge_agent,
    create_log_agent,
    create_model_client,
    create_qa_agent,
    create_query_agent,
    create_resolution_agent,
)
from .config import Settings, get_settings
from .ticket_log import TicketLogger


def build_support_team(
    settings: Settings | None = None,
    logger: TicketLogger | None = None,
    mode: Literal["round_robin", "selector"] = "round_robin",
):
    """Create an AutoGen multi-agent team for customer support ticket processing."""
    cfg = settings or get_settings()
    ticket_logger = logger or TicketLogger()
    client = create_model_client(cfg)

    async def record_ticket(status: str, escalation_reason: str, handoff_note: str = "") -> str:
        """Record the ticket outcome and emit the LOGGED termination token."""
        payload = {
            "logged": True,
            "status": status,
            "escalation_reason": escalation_reason,
            "handoff_note": handoff_note,
            "marker": "LOGGED",
        }
        return json.dumps(payload) + " LOGGED"

    agents = [
        create_query_agent(client),
        create_knowledge_agent(client),
        create_resolution_agent(client),
        create_qa_agent(client),
        create_log_agent(client, record_ticket),
    ]

    termination = TextMentionTermination("LOGGED") | MaxMessageTermination(max_messages=12)

    if mode == "selector":
        return SelectorGroupChat(
            participants=agents,
            model_client=client,
            termination_condition=termination,
        )
    return RoundRobinGroupChat(
        participants=agents,
        termination_condition=termination,
    )
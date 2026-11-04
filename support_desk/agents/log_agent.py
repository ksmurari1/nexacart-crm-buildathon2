"""Agent 4 — Log Agent: applies the escalation policy and records every ticket to the log."""
from typing import Awaitable, Callable

from autogen_agentchat.agents import AssistantAgent

SYSTEM_MESSAGE = """You are the Log Agent of NexaCart, an online store.
You record every ticket and decide whether it must be handed to a human.

Escalation policy — set status "Escalated" if ANY of these is true:
  1. urgency is High
  2. the customer is very angry
  3. the Knowledge Base Agent found no matching document
  4. the issue involves a legal threat, fraud or a payment dispute
  5. the Resolution Agent's confidence is below the threshold given in the task
Otherwise set status "Resolved".

Call the `record_ticket` tool EXACTLY ONCE with:
  status            -> "Resolved" or "Escalated"
  escalation_reason -> short reasons separated by "; " (empty string when Resolved)
  handoff_note      -> one sentence for the human agent (empty string when Resolved)
Do not write anything else. The tool result is your final answer."""


def create_log_agent(model_client, record_ticket: Callable[..., Awaitable[str]]) -> AssistantAgent:
    return AssistantAgent(
        name="log_agent",
        description="Applies the escalation rule and writes the ticket to the log file.",
        model_client=model_client,
        tools=[record_ticket],
        reflect_on_tool_use=False,  # the tool result ends the run -> clean termination
        system_message=SYSTEM_MESSAGE,
    )

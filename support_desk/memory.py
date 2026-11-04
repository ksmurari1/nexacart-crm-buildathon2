"""Lightweight persistent customer/ticket memory for NexaCart.

Stores a bounded history of ticket summaries in JSON. This is deliberately
separate from the policy vector store: policy retrieval remains in the RAG KB.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_DIR = Path(BASE_DIR) / "data"
MEMORY_FILE = MEMORY_DIR / "customer_memory.json"
MAX_RECORDS_PER_KEY = 5


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _load_memory() -> dict[str, list[dict[str, Any]]]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Fail safely: a corrupted memory file should not block support.
        return {}


def _save_memory(data: dict[str, list[dict[str, Any]]]) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = MEMORY_FILE.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_file.replace(MEMORY_FILE)


def _memory_keys(customer_name: str = "", order_id: str = "") -> list[str]:
    keys = []
    order = _normalize(order_id)
    customer = _normalize(customer_name)
    if order:
        keys.append(f"order:{order}")
    if customer:
        keys.append(f"customer:{customer}")
    return keys


def find_memory(
    customer_name: str = "",
    order_id: str = "",
    limit: int = MAX_RECORDS_PER_KEY,
) -> list[dict[str, Any]]:
    """Return recent matching ticket memories, newest first.

    Order ID matches take precedence. Customer-name matching is a fallback.
    """
    data = _load_memory()
    keys = _memory_keys(customer_name, order_id)
    order_key = keys[0] if keys and keys[0].startswith("order:") else None
    customer_key = next((k for k in keys if k.startswith("customer:")), None)

    records = data.get(order_key, []) if order_key else []
    if not records and customer_key:
        records = data.get(customer_key, [])

    # Newest records first; return a bounded, shallow copy.
    return list(reversed(records[-max(1, limit):]))


def remember_ticket(ticket: dict[str, Any]) -> int:
    """Persist a privacy-conscious summary of a completed/escalated ticket.

    Returns the number of memory keys updated. Avoid storing full conversation
    transcripts or sensitive payment details.
    """
    customer_name = str(ticket.get("customer_name", "") or "").strip()
    order_id = str(ticket.get("order_id", "") or "").strip()
    keys = _memory_keys(customer_name, order_id)
    if not keys:
        return 0

    record = {
        "timestamp": str(ticket.get("timestamp", "") or ""),
        "ticket_id": str(ticket.get("ticket_id", "") or ""),
        "order_id": order_id,
        "category": str(ticket.get("category", "") or ""),
        "urgency": str(ticket.get("urgency", "") or ""),
        "sentiment": str(ticket.get("sentiment", "") or ""),
        "status": str(ticket.get("status", "") or ""),
        "summary": str(ticket.get("summary", "") or ticket.get("complaint", "") or "")[:500],
        "resolution_summary": str(
            ticket.get("resolution_summary", "") or ticket.get("response", "") or ""
        )[:700],
        "escalation_reason": str(ticket.get("escalation_reason", "") or "")[:300],
    }

    data = _load_memory()
    for key in keys:
        records = data.setdefault(key, [])
        # Avoid duplicate writes when both order and customer keys are updated.
        if not records or records[-1].get("ticket_id") != record["ticket_id"]:
            records.append(record)
        data[key] = records[-MAX_RECORDS_PER_KEY:]
    _save_memory(data)
    return len(keys)


def format_memory_context(records: list[dict[str, Any]]) -> str:
    """Format retrieved memory as compact, clearly historical context."""
    if not records:
        return ""
    lines = [
        "HISTORICAL CUSTOMER/TICKET CONTEXT (not current policy; verify with KB):"
    ]
    for item in records:
        lines.append(
            "- "
            + f"Ticket {item.get('ticket_id') or 'unknown'} | "
            + f"Order {item.get('order_id') or 'not provided'} | "
            + f"Status: {item.get('status') or 'unknown'} | "
            + f"Category: {item.get('category') or 'unknown'} | "
            + f"Summary: {item.get('summary') or 'not available'} | "
            + f"Prior response: {item.get('resolution_summary') or 'not available'}"
        )
    lines.append(
        "Use this only to understand continuity. Do not treat prior responses "
        "as policy evidence. If the issue is unresolved, repeated, or sensitive, "
        "consider escalation."
    )
    return "\n".join(lines)

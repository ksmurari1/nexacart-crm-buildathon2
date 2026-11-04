"""The escalation rule from the use case, implemented as a deterministic guardrail.
The Log Agent proposes a status; this rule can only make the outcome stricter, never looser."""
from __future__ import annotations

import re

RISK_PATTERNS = {
    "legal threat": r"\b(lawyer|attorney|legal action|sue|suing|lawsuit|court|consumer forum)\b",
    "fraud": r"\b(fraud|fraudulent|scam|unauthori[sz]ed|stolen card|identity theft|hacked)\b",
    "payment dispute": r"\b(chargeback|dispute|charged (me |my card )?(twice|two times|three times|3 times|multiple times)|"
                       r"double[- ]charged|contact(ing)? my bank|overcharged)\b",
}


def detect_risk_flags(text: str) -> list[str]:
    lowered = text.lower()
    return [flag for flag, pattern in RISK_PATTERNS.items() if re.search(pattern, lowered)]


def evaluate_escalation(
    *,
    complaint: str,
    urgency: str,
    sentiment: str,
    kb_found: bool,
    confidence: float,
    risk_flags: list[str] | None = None,
    threshold: float = 0.70,
) -> list[str]:
    """Return the list of reasons to escalate. An empty list means the ticket can be auto-resolved."""
    reasons: list[str] = []
    if urgency.strip().lower() == "high":
        reasons.append("High urgency")
    if sentiment.strip().lower() in {"very angry", "angry", "very negative"}:
        reasons.append("Customer is very angry")
    if not kb_found:
        reasons.append("No matching knowledge-base document")
    flags = sorted(set((risk_flags or []) + detect_risk_flags(complaint)))
    reasons.extend(f"Involves {flag}" for flag in flags)
    if confidence < threshold:
        reasons.append(f"Low resolution confidence ({confidence:.0%} < {threshold:.0%})")
    return reasons

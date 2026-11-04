
"""Tests for Pydantic validation models."""

import pytest
from pydantic import ValidationError

from support_desk.models import (
    ComplaintInput,
    AgentAnalysis,
    ResolutionOutput,
)


# ── ComplaintInput ──────────────────────────────────────────────

def test_valid_complaint():
    complaint = ComplaintInput(
        complaint="My order has not arrived.",
        customer_name="Murari",
        order_id="ORD-12345",
    )
    assert complaint.customer_name == "Murari"
    assert complaint.order_id == "ORD-12345"


def test_empty_complaint_rejected():
    with pytest.raises(ValidationError):
        ComplaintInput(complaint="")


def test_short_complaint_rejected():
    with pytest.raises(ValidationError):
        ComplaintInput(complaint="Hi")


# ── AgentAnalysis ──────────────────────────────────────────────

def test_valid_agent_analysis():
    analysis = AgentAnalysis(
        category="Shipping & Delivery",
        urgency="Medium",
        sentiment="Negative",
        language="English",
        risk_flags=[],
        order_id="ORD-12345",
        summary="Customer reports a delayed delivery.",
        search_query="shipping delivery delayed order tracking",
    )
    assert analysis.urgency == "Medium"


def test_invalid_urgency_rejected():
    with pytest.raises(ValidationError):
        AgentAnalysis(
            category="Shipping & Delivery",
            urgency="Critical",
            sentiment="Negative",
            language="English",
            summary="Delayed order",
            search_query="shipping delay",
        )


def test_invalid_category_rejected():
    with pytest.raises(ValidationError):
        AgentAnalysis(
            category="Technical Support",
            urgency="Low",
            sentiment="Neutral",
            language="English",
            summary="Product question",
            search_query="product information",
        )


# ── ResolutionOutput ───────────────────────────────────────────

def test_valid_resolution():
    resolution = ResolutionOutput(
        reply="Your refund has been initiated.",
        confidence=0.95,
        cited_passages=["refund_policy_01"],
        gaps="",
    )
    assert resolution.confidence == 0.95


def test_confidence_above_one_rejected():
    with pytest.raises(ValidationError):
        ResolutionOutput(
            reply="Refund initiated.",
            confidence=1.5,
        )


def test_negative_confidence_rejected():
    with pytest.raises(ValidationError):
        ResolutionOutput(
            reply="Refund initiated.",
            confidence=-0.2,
        )


def test_empty_reply_rejected():
    with pytest.raises(ValidationError):
        ResolutionOutput(
            reply="",
            confidence=0.8,
        )

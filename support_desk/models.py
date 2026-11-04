
"""Pydantic models for validating NexaCart customer support data."""

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from .config import CATEGORIES, URGENCY_LEVELS, SENTIMENTS


class ComplaintInput(BaseModel):
    """Validates customer complaint input."""

    model_config = ConfigDict(str_strip_whitespace=True)

    complaint: str = Field(min_length=5, max_length=5000)
    customer_name: str = Field(default="", max_length=100)
    order_id: str = Field(default="", max_length=50)


class AgentAnalysis(BaseModel):
    """Validates structured output from the Customer Query Agent."""

    category: Literal[
        "Shipping & Delivery",
        "Returns & Refunds",
        "Damaged or Defective Product",
        "Account & Login",
        "Billing & Payments",
        "Product Inquiry",
        "Other",
    ]

    urgency: Literal["Low", "Medium", "High"]

    sentiment: Literal[
        "Positive",
        "Neutral",
        "Negative",
        "Very Angry",
    ]

    language: str = Field(min_length=2, max_length=50)
    risk_flags: list[str] = Field(default_factory=list)
    order_id: str = Field(default="", max_length=50)
    summary: str = Field(min_length=1, max_length=500)
    search_query: str = Field(min_length=1, max_length=1000)


class ResolutionOutput(BaseModel):
    """Validates the Resolution Agent's proposed customer response."""

    reply: str = Field(min_length=1, max_length=10000)
    confidence: float = Field(ge=0.0, le=1.0)
    cited_passages: list[str] = Field(default_factory=list)
    gaps: str = Field(default="", max_length=2000)

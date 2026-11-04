"""Central configuration. Every secret comes from the environment / .env — never from code."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

KB_DIR = Path(os.getenv("KB_DIR", ROOT / "knowledge_base"))
LOG_DIR = Path(os.getenv("LOG_DIR", ROOT / "logs"))
SAMPLES_FILE = ROOT / "data" / "sample_complaints.json"

CATEGORIES = [
    "Shipping & Delivery",
    "Returns & Refunds",
    "Damaged or Defective Product",
    "Account & Login",
    "Billing & Payments",
    "Product Inquiry",
    "Other",
]
URGENCY_LEVELS = ["Low", "Medium", "High"]
SENTIMENTS = ["Positive", "Neutral", "Negative", "Very Angry"]


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    base_url: str | None
    confidence_threshold: float
    kb_top_k: int
    agent_timeout_s: int

    @property
    def llm_enabled(self) -> bool:
        return bool(self.api_key)


def get_settings() -> Settings:
    return Settings(
        api_key=os.getenv("OPENAI_API_KEY") or None,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.70")),
        kb_top_k=int(os.getenv("KB_TOP_K", "4")),
        agent_timeout_s=int(os.getenv("AGENT_TIMEOUT_SECONDS", "60")),
    )

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from support_desk.config import get_settings  # noqa: E402
from support_desk.pipeline import SupportPipeline  # noqa: E402
from support_desk.ticket_log import TicketLogger  # noqa: E402


@pytest.fixture
def logger(tmp_path):
    return TicketLogger(tmp_path)


@pytest.fixture
def offline_pipeline(logger, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    return SupportPipeline(settings=get_settings(), logger=logger)

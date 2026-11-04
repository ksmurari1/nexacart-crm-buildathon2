"""Deterministic tests — no API key or network required.  Run: pytest -q"""
import asyncio

from support_desk.escalation import detect_risk_flags, evaluate_escalation
from support_desk.knowledge_base import get_kb, search_knowledge_base
from support_desk.pipeline import parse_json
from support_desk.evaluation import evaluate_retrieval
from support_desk.ticket_log import COLUMNS


def test_kb_loads_all_documents():
    names = {d["name"] for d in get_kb().documents()}
    assert {"shipping_policy.pdf", "refund_policy.pdf", "account_and_login.pdf", "product_faq.pdf"} <= names


def test_kb_retrieves_the_right_document():
    cases = {
        "I forgot my password and can't log in": "account_and_login.pdf",
        "return shoes refund": "refund_policy.pdf",
        "order late delivery tracking": "shipping_policy.pdf",
        "blender broken replacement": "product_faq.pdf",
    }
    for query, source in cases.items():
        assert get_kb().search(query)[0][0].source == source, query


def test_kb_no_match_for_unrelated_query():
    assert search_knowledge_base("quantum astrophysics telescope").startswith("NO_MATCH")


def test_risk_flags():
    flags = detect_risk_flags("You charged my card three times! I'm contacting my bank and a lawyer.")
    assert {"legal threat", "payment dispute"} <= set(flags)


def test_escalation_rule_each_trigger():
    base = dict(complaint="hello", urgency="Low", sentiment="Neutral", kb_found=True, confidence=0.9)
    assert evaluate_escalation(**base) == []
    assert evaluate_escalation(**{**base, "urgency": "High"})
    assert evaluate_escalation(**{**base, "sentiment": "Very Angry"})
    assert evaluate_escalation(**{**base, "kb_found": False})
    assert evaluate_escalation(**{**base, "confidence": 0.4})
    assert evaluate_escalation(**{**base, "complaint": "this is fraud"})


def test_parse_json_tolerates_fences():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json("no json here") == {}


def test_offline_pipeline_resolves_and_logs(offline_pipeline, logger):
    steps = []
    ticket = asyncio.run(offline_pipeline.run("I forgot my password and can't log in.", "Mei", on_step=steps.append))
    assert [s["key"] for s in steps if s["status"] != "running"] == [
        "query_agent", "knowledge_agent", "resolution_agent", "qa_agent", "log_agent"]
    assert ticket["status"] == "Resolved" and "account_and_login.pdf" in ticket["kb_sources"]
    df = logger.read()
    assert list(df.columns) == COLUMNS and len(df) == 1 and df.iloc[0]["ticket_id"] == ticket["ticket_id"]


def test_offline_pipeline_escalates_legal_threat(offline_pipeline):
    ticket = asyncio.run(offline_pipeline.run(
        "You charged my card three times! Fix this now or I'm contacting my bank and a lawyer."))
    assert ticket["status"] == "Escalated" and "legal threat" in ticket["escalation_reason"]
    assert ticket["ticket_id"] in ticket["response"]


def test_excel_export(offline_pipeline, logger):
    asyncio.run(offline_pipeline.run("Where is my order? It was supposed to arrive yesterday."))
    assert logger.to_excel_bytes(logger.read())[:2] == b"PK"  # xlsx is a zip container


def test_pdf_ingestion_preserves_page_provenance():
    kb = get_kb()
    pdf_passages = [p for p in kb.passages if p.source.endswith(".pdf")]
    assert pdf_passages
    assert all(p.page is not None for p in pdf_passages)


def test_offline_qa_rejects_missing_evidence():
    from support_desk.pipeline import SupportPipeline
    weak = {"resolution": {"reply": "A reply without a source.", "confidence": 0.8, "cited_passages": []},
            "knowledge": {"passages": []}}
    qa = SupportPipeline._offline_qa(weak)
    assert not qa["passed"] and not qa["grounded"]


def test_rag_evaluation_benchmark():
    result = evaluate_retrieval(get_kb(), top_k=3)
    assert result["hit_at_1"] >= 0.90
    assert result["hit_at_k"] == 1.0
    assert result["no_match_accuracy"] == 1.0
    assert result["cases"] >= 10


def test_escalated_ticket_enters_human_review_queue(tmp_path):
    from support_desk.ticket_log import HumanReviewStore, TicketLogger
    logger = TicketLogger(tmp_path)
    logger.record({
        "ticket_id": "TKT-REVIEW-001", "timestamp": "2026-11-02T10:00:00Z",
        "customer_name": "Test Customer", "order_id": "ORD-1234", "complaint": "Payment dispute",
        "category": "Billing & Payments", "urgency": "High", "sentiment": "Very Angry",
        "kb_sources": ["payments_and_billing.pdf"], "response": "We have escalated your case.",
        "confidence": 0.4, "status": "Escalated", "escalation_reason": "Payment dispute",
    })
    review = HumanReviewStore(tmp_path).read()
    assert len(review) == 1 and review.iloc[0]["review_status"] == "Pending"
    store = HumanReviewStore(tmp_path)
    assert store.update("TKT-REVIEW-001", review_status="Approved", reviewer="QA Tester",
                       review_notes="Verified", approved_response="Reviewed response")
    updated = store.read().iloc[0]
    assert updated["review_status"] == "Approved"
    assert updated["approved_response"] == "Reviewed response"

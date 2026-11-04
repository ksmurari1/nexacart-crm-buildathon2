"""The support workflow: Query Agent -> Knowledge Base Agent -> Resolution Agent -> Log Agent.

Agents run strictly in this order. Each agent run is a single AutoGen turn with a timeout, so the
workflow always terminates cleanly. Every step is streamed to an optional `on_step` callback so a
UI can render each agent's output as it happens. Without an API key the same pipeline runs in a
transparent offline mode (keyword rules + the same knowledge base) so the app is always demo-able.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from autogen_agentchat.messages import ToolCallRequestEvent

from .agents import (
    create_knowledge_agent,
    create_log_agent,
    create_model_client,
    create_query_agent,
    create_resolution_agent,
    create_qa_agent,
)
from .config import CATEGORIES, SENTIMENTS, URGENCY_LEVELS, Settings, get_settings
from .memory import find_memory, format_memory_context, remember_ticket
from .escalation import detect_risk_flags, evaluate_escalation
from .knowledge_base import KnowledgeBase, get_kb
from .models import ComplaintInput, AgentAnalysis, ResolutionOutput
from .ticket_log import TicketLogger

AGENTS = {
    "query_agent": ("Customer Query Agent", "Understands category, urgency and sentiment"),
    "knowledge_agent": ("Knowledge Base Agent", "Retrieves only the relevant policy passages"),
    "resolution_agent": ("Resolution Agent", "Writes a grounded, polite reply"),
    "qa_agent": ("Quality Assurance Agent", "Checks grounding, citations, and response quality"),
    "log_agent": ("Log Agent", "Applies escalation rule and records the ticket"),
}
HANDOFF_NOTE = (
    "Your ticket {ticket_id} has been escalated to a senior NexaCart support specialist, "
    "who will contact you within 4 business hours."
)
StepCallback = Callable[[dict], Any]


# ----------------------------------------------------------------------------- helpers
def new_ticket_id() -> str:
    return f"TKT-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def parse_json(text: str) -> dict:
    """Tolerant JSON extraction: accepts fenced blocks or prose around the object."""
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def last_text(result) -> str:
    for message in reversed(result.messages):
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip() and getattr(message, "source", "") != "user":
            return content.strip()
    return ""


def _pick(value: Any, allowed: list[str], default: str) -> str:
    lookup = {a.lower(): a for a in allowed}
    return lookup.get(str(value or "").strip().lower(), default)


def _text(value: Any) -> str:
    return " ".join(map(str, value)) if isinstance(value, list) else str(value or "")


def normalize_analysis(data: dict, complaint: str, order_id: str) -> dict:
    flags = [f for f in data.get("risk_flags") or [] if isinstance(f, str)]
    detected_lang = detect_language(complaint)
    raw_lang = str(data.get("language") or "").strip()
    language = raw_lang if raw_lang and detected_lang == "English" else detected_lang
    raw_query = _text(data.get("search_query")) or complaint
    return {
        "category": _pick(data.get("category"), CATEGORIES, "Other"),
        "urgency": _pick(data.get("urgency"), URGENCY_LEVELS, "Medium"),
        "sentiment": _pick(data.get("sentiment"), SENTIMENTS, "Neutral"),
        "language": language,
        "risk_flags": sorted(set(f.lower() for f in flags) | set(detect_risk_flags(complaint))),
        "order_id": order_id or str(data.get("order_id") or ""),
        "summary": str(data.get("summary") or complaint[:160]),
        "search_query": expand_multilingual_query(raw_query),
    }


# ------------------------------------------------------------------ offline (no API key)
KEYWORDS = {
    "Billing & Payments": "charge charged card payment billing invoice bank double twice promo coupon code",
    "Account & Login": "password login log account email locked reset sign verification otp",
    "Damaged or Defective Product": "broken damaged defective cracked shattered faulty stopped working replacement",
    "Returns & Refunds": "return refund exchange money back size wrong item",
    "Shipping & Delivery": "where order delivery arrive shipping tracking package late courier address",
    "Product Inquiry": "sell gift card bulk available stock warranty size product",
}
ANGRY_WORDS = r"\b(useless|unacceptable|ridiculous|worst|scam|furious|fix this now|right now|terrible|disgusting)\b"
CUSTOM_REQUEST = r"\b(bulk|wholesale|corporate|reseller|partnership|custom branding|\d{3,} employees)\b"
NEGATIVE_WORDS = r"\b(broken|late|can't|cannot|damaged|wrong|disappointed|still|never|missing|not)\b"


def offline_analysis(complaint: str, order_id: str) -> dict:
    text = complaint.lower()
    scores = {c: sum(w in text for w in words.split()) for c, words in KEYWORDS.items()}
    category = max(scores, key=scores.get) if max(scores.values()) else "Other"
    flags = detect_risk_flags(complaint)
    angry = bool(re.search(ANGRY_WORDS, text)) or complaint.count("!") >= 2 or "legal threat" in flags
    sentiment = "Very Angry" if angry else "Negative" if re.search(NEGATIVE_WORDS, text) else "Neutral"
    urgency = "High" if (angry or flags) else "Medium" if category not in ("Product Inquiry", "Other") else "Low"
    found_order = re.search(r"\b(ORD-?\d{3,})\b", complaint, re.I)
    return normalize_analysis(
        {"category": category, "urgency": urgency, "sentiment": sentiment, "risk_flags": flags,
         "order_id": found_order.group(1).upper() if found_order else "",
         "summary": complaint[:160], "search_query": complaint},
        complaint, order_id,
    )


def offline_resolution(customer_name: str, passages: list[dict], complaint: str = "") -> dict:
    if not passages:
        return {"reply": "", "confidence": 0.0, "cited_passages": [], "gaps": "No matching policy found."}
    top = passages[0]
    body = re.sub(r"\n{2,}", "\n", top["text"]).strip()
    reply = (
        f"Hi {customer_name or 'there'},\n\nThank you for contacting NexaCart. Here is what our "
        f"{top['section']} policy says:\n\n{body}\n\nIf anything is still unclear, simply reply to this "
        "message.\n\nNexaCart Support"
    )
    if re.search(CUSTOM_REQUEST, complaint.lower()):  # bulk / B2B requests are not covered by the KB
        return {"reply": reply, "confidence": 0.4, "cited_passages": [top["id"]],
                "gaps": "Custom or bulk business request is not covered by the knowledge base."}
    return {"reply": reply, "confidence": 0.80,
            "cited_passages": [top["id"]], "gaps": ""}


# ----------------------------------------------------------------------------- pipeline
class SupportPipeline:
    def __init__(self, settings: Settings | None = None, logger: TicketLogger | None = None,
                 kb: KnowledgeBase | None = None):
        self.settings = settings or get_settings()
        self.logger = logger or TicketLogger()
        self.kb = kb or get_kb()

    async def run(self, complaint: str, customer_name: str = "", order_id: str = "",
                  on_step: StepCallback | None = None, ticket_id: str | None = None) -> dict:
        
        validated_input = ComplaintInput(
            complaint=complaint or "",
            customer_name=customer_name or "",
            order_id=order_id or "",
        )

        complaint = validated_input.complaint
        customer_name = validated_input.customer_name
        order_id = validated_input.order_id

        # Persistent ticket memory is historical context, never policy evidence.
        prior_memory = find_memory(customer_name=customer_name, order_id=order_id)
        memory_context = format_memory_context(prior_memory)

        llm = self.settings.llm_enabled
        ticket: dict[str, Any] = {
            "ticket_id": ticket_id or new_ticket_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "customer_name": customer_name.strip(), "order_id": order_id.strip().upper(),
            "complaint": complaint, "mode": "autogen" if llm else "offline", "steps": [], "errors": [],
            "memory_context": memory_context,
            "memory_records_found": len(prior_memory),
        }

        async def step(key: str, work: Callable[[], Any], fallback: Callable[[], Any]) -> Any:
            name, role = AGENTS[key]
            record = {"key": key, "name": name, "role": role, "status": "running", "output": None,
                      "duration_s": None, "error": None}
            await self._emit(on_step, record)
            started = time.perf_counter()
            try:
                output = await asyncio.wait_for(work(), self.settings.agent_timeout_s)
                record["status"] = "done"
            except Exception as exc:  # degrade gracefully, escalate later
                ticket["errors"].append(f"{name} failed")
                record.update(status="error", error=f"{type(exc).__name__}: {exc}")
                output = fallback()
            record.update(output=output, duration_s=round(time.perf_counter() - started, 2))
            ticket["steps"].append(record)
            await self._emit(on_step, dict(record))
            return output

        client = create_model_client(self.settings) if llm else None
        try:
            analysis = await step(
                "query_agent",
                (lambda: self._query(client, ticket)) if llm else self._wrap(offline_analysis, complaint, order_id),
                lambda: offline_analysis(complaint, order_id),
            )
            ticket.update(analysis=analysis, order_id=ticket["order_id"] or analysis["order_id"])
            knowledge = await step(
                "knowledge_agent",
                (lambda: self._knowledge(client, ticket)) if llm else self._wrap(self._offline_knowledge, ticket),
                lambda: self._offline_knowledge(ticket),
            )
            ticket["knowledge"] = knowledge
            resolution = await step(
                "resolution_agent",
                (lambda: self._resolution(client, ticket)) if llm
                else self._wrap(offline_resolution, customer_name, knowledge["passages"], complaint),
                lambda: offline_resolution(customer_name, knowledge["passages"], complaint),
            )
            ticket["resolution"] = resolution
            qa = await step(
                "qa_agent",
                (lambda: self._qa(client, ticket)) if llm else self._wrap(self._offline_qa, ticket),
                lambda: self._offline_qa(ticket),
            )
            ticket["qa"] = qa
            if not qa.get("passed", False):
                resolution["confidence"] = min(float(resolution.get("confidence", 0.0)), float(qa.get("quality_score", 0.0)))
                resolution["gaps"] = "; ".join(filter(None, [resolution.get("gaps", ""), "; ".join(qa.get("issues", []))]))
            await step(
                "log_agent",
                (lambda: self._log(client, ticket)) if llm else self._wrap(self._offline_log, ticket),
                lambda: self._offline_log(ticket),
            )
        finally:
            if client is not None:
                await client.close()
        return self._public(ticket)

    # ---------------------------------------------------------------- agent stages (LLM)
    async def _query(self, client, t: dict) -> dict:
        task = (f"Customer name: {t['customer_name'] or 'not given'}\nOrder ID: {t['order_id'] or 'not given'}\n"
                f"Complaint:\n\"\"\"{t['complaint']}\"\"\"")
        result = await create_query_agent(client).run(task=task)
        raw_data = normalize_analysis(
            parse_json(last_text(result)),
            t["complaint"],
            t["order_id"],
        )

        validated = AgentAnalysis.model_validate(raw_data)
        return validated.model_dump()

    async def _knowledge(self, client, t: dict) -> dict:
        a = t["analysis"]
        task = (f"Complaint: \"\"\"{t['complaint']}\"\"\"\nCategory: {a['category']}\n"
                f"Problem summary: {a['summary']}\nSuggested keywords: {a['search_query']}")
        result = await create_knowledge_agent(client).run(task=task)
        searches = [json.loads(call.arguments).get("query", "") for m in result.messages
                    if isinstance(m, ToolCallRequestEvent) for call in m.content]
        data = parse_json(last_text(result))
        ids = [i for i in dict.fromkeys(data.get("passage_ids") or []) if self.kb.get(str(i))]
        passages = [self.kb.get(i).to_dict() for i in ids]  # verbatim KB text, never model text
        return {"found": bool(data.get("found", True)) and bool(passages), "passages": passages,
                "searches": searches, "reasoning": str(data.get("reasoning", ""))}

    async def _resolution(self, client, t: dict) -> dict:
        passages = t["knowledge"]["passages"]
        context = "\n\n".join(f"[{p['id']}] ({p['source']} > {p['section']})\n{p['text']}" for p in passages)
        task = (f"Customer name: {t['customer_name'] or 'not given'}\nOrder ID: {t['order_id'] or 'not given'}\n"
                f"Complaint: \"\"\"{t['complaint']}\"\"\"\nAnalysis: {json.dumps(t['analysis'])}\n\n"
                f"POLICY PASSAGES:\n{context or 'NONE - no matching policy was found.'}")
        data = parse_json(last_text(await create_resolution_agent(client).run(task=task)))
        valid = {p["id"] for p in passages}
        try:
            confidence = max(0.0, min(1.0, float(data.get("confidence", 0))))
        except (TypeError, ValueError):
            confidence = 0.0
        
        raw_output = {
            "reply": str(data.get("reply") or "").strip(),
            "confidence": round(confidence, 2),
            "cited_passages": [
                c for c in data.get("cited_passages") or [] if c in valid
            ],
            "gaps": str(data.get("gaps") or ""),
        }

        validated = ResolutionOutput.model_validate(raw_output)
        return validated.model_dump()


    async def _qa(self, client, t: dict) -> dict:
        passages=t["knowledge"]["passages"]
        evidence="\n\n".join(f"[{p['id']}] {p['text']}" for p in passages)
        task=(f"COMPLAINT: {t['complaint']}\nPROPOSED RESPONSE: {t['resolution']['reply']}\\n"
              f"CITATIONS: {t['resolution']['cited_passages']}\nPOLICY EVIDENCE:\\n{evidence}")
        data=parse_json(last_text(await create_qa_agent(client).run(task=task)))
        valid={p["id"] for p in passages}
        citations=[c for c in data.get("valid_citations",[]) if c in valid]
        passed=bool(data.get("passed")) and bool(data.get("grounded")) and bool(t["resolution"]["reply"]) and (
            not t["resolution"]["cited_passages"] or len(citations)==len(t["resolution"]["cited_passages"]))
        try: score=max(0.0,min(1.0,float(data.get("quality_score",0.0))))
        except (TypeError,ValueError): score=0.0
        return {"passed":passed,"grounded":bool(data.get("grounded")),"valid_citations":citations,
                "issues":[str(x) for x in data.get("issues",[])],"quality_score":round(score,2)}

    @staticmethod
    def _offline_qa(t: dict) -> dict:
        r=t["resolution"]; passages=t["knowledge"]["passages"]
        valid={p["id"] for p in passages}
        cites=[c for c in r.get("cited_passages",[]) if c in valid]
        issues=[]
        if not r.get("reply"): issues.append("Response is empty.")
        if not passages: issues.append("No evidence retrieved; human review required.")
        if r.get("cited_passages") and len(cites)!=len(r["cited_passages"]): issues.append("Invalid citation detected.")
        grounded=bool(passages) and bool(cites) and len(cites)==len(r.get("cited_passages",[]))
        score=min(float(r.get("confidence",0.0)),0.85) if grounded else 0.25
        return {"passed":grounded and bool(r.get("reply")),"grounded":grounded,
                "valid_citations":cites,"issues":issues,"quality_score":round(score,2)}

    async def _log(self, client, t: dict) -> dict:
        outcome: dict = {}

        async def record_ticket(status: str, escalation_reason: str, handoff_note: str = "") -> str:
            """Record the ticket in the NexaCart ticket log (CSV + TXT). status: 'Resolved' or 'Escalated'."""
            outcome.update(self._finalize(t, status, escalation_reason, handoff_note))
            return json.dumps({"logged": True, "ticket_id": t["ticket_id"], "status": outcome["status"],
                               "escalation_reason": outcome["escalation_reason"]})

        a, k, r = t["analysis"], t["knowledge"], t["resolution"]
        task = (f"Ticket {t['ticket_id']}\nurgency: {a['urgency']}\nsentiment: {a['sentiment']}\n"
                f"risk_flags: {a['risk_flags']}\nknowledge_found: {k['found']}\n"
                f"resolution_confidence: {r['confidence']}\nconfidence_threshold: {self.settings.confidence_threshold}\n"
                f"category: {a['category']}\nsummary: {a['summary']}")
        await create_log_agent(client, record_ticket).run(task=task)
        if not outcome:  # the agent did not call its tool -> the pipeline still guarantees a log row
            t["errors"].append("Log Agent did not call record_ticket")
            outcome.update(self._finalize(t, "Resolved", "", ""))
        return outcome

    # -------------------------------------------------------------------- deterministic
    def _offline_knowledge(self, t: dict) -> dict:
        a = t["analysis"]
        hits = self.kb.search(f"{a['category']} {t['complaint']}", top_k=3)
        return {"found": bool(hits), "passages": [p.to_dict(s) for p, s in hits],
                "searches": [t["complaint"][:80]], "reasoning": "Offline BM25 keyword retrieval."}

    def _offline_log(self, t: dict) -> dict:
        return self._finalize(t, "Resolved", "", "")

    def _finalize(self, t: dict, agent_status: str, agent_reason: str, handoff_note: str) -> dict:
        a, k, r = t["analysis"], t["knowledge"], t["resolution"]
        reasons = evaluate_escalation(
            complaint=t["complaint"], urgency=a["urgency"], sentiment=a["sentiment"], kb_found=k["found"],
            confidence=r["confidence"], risk_flags=a["risk_flags"], threshold=self.settings.confidence_threshold,
        )
        if not reasons and agent_status.strip().lower() == "escalated":
            reasons = [s.strip() for s in agent_reason.split(";") if s.strip()] or ["Flagged by Log Agent"]
        qa = t.get("qa", {})
        if qa and not qa.get("passed", False):
            reasons.append("QA verification failed")
        reasons += [e for e in t["errors"] if e not in reasons]
        status = "Escalated" if reasons else "Resolved"
        reply = r["reply"] or f"Hi {t['customer_name'] or 'there'},\n\nThank you for contacting NexaCart."
        if status == "Escalated":
            reply = f"{reply.rstrip()}\n\n{HANDOFF_NOTE.format(ticket_id=t['ticket_id'])}"
        t.update(status=status, escalation_reason="; ".join(reasons), response=reply,
                 handoff_note=handoff_note if status == "Escalated" else "")
        if not t.get("logged"):
            t["logged"] = True
            self.logger.record({
                **t, "category": a["category"], "urgency": a["urgency"], "sentiment": a["sentiment"],
                "kb_sources": sorted({p["source"] for p in k["passages"]}), "confidence": r["confidence"],
            })
            # Persist a compact memory record only after the ticket reaches final disposition.
            remember_ticket({
                "ticket_id": t["ticket_id"],
                "timestamp": t["timestamp"],
                "customer_name": t["customer_name"],
                "order_id": t["order_id"],
                "category": a["category"],
                "urgency": a["urgency"],
                "sentiment": a["sentiment"],
                "status": status,
                "summary": a["summary"],
                "response": reply,
                "escalation_reason": t["escalation_reason"],
            })
        return {"agent_proposed_status": agent_status, "status": status,
                "escalation_reason": t["escalation_reason"], "handoff_note": t["handoff_note"],
                "guardrail_override": agent_status.strip().lower() != status.lower(),
                "log_file": str(self.logger.csv_path.name)}

    # ------------------------------------------------------------------------ plumbing
    @staticmethod
    def _wrap(fn: Callable, *args) -> Callable[[], Any]:
        async def runner():
            return fn(*args)
        return runner

    @staticmethod
    async def _emit(callback: StepCallback | None, record: dict) -> None:
        if callback is not None:
            result = callback(dict(record))
            if inspect.isawaitable(result):
                await result

    @staticmethod
    def _public(t: dict) -> dict:
        a, k, r = t["analysis"], t["knowledge"], t["resolution"]
        return {
            "ticket_id": t["ticket_id"], "timestamp": t["timestamp"], "mode": t["mode"],
            "memory_records_found": t.get("memory_records_found", 0),
            "customer_name": t["customer_name"], "order_id": t["order_id"], "complaint": t["complaint"],
            "category": a["category"], "urgency": a["urgency"], "sentiment": a["sentiment"],
            "risk_flags": a["risk_flags"], "summary": a["summary"],
            "kb_found": k["found"], "kb_sources": sorted({p["source"] for p in k["passages"]}),
            "passages": k["passages"], "response": t["response"], "confidence": r["confidence"], "qa": t.get("qa", {}),
            "status": t["status"], "escalation_reason": t["escalation_reason"],
            "handoff_note": t.get("handoff_note", ""), "steps": t["steps"],
        }


async def run_ticket(complaint: str, customer_name: str = "", order_id: str = "",
                     on_step: StepCallback | None = None) -> dict:
    """Convenience entry point used by the Streamlit app and the CLI."""
    return await SupportPipeline().run(complaint, customer_name, order_id, on_step)

def detect_language(text: str) -> str:
    """Detect customer complaint language using Unicode script ranges and common lexical markers."""
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "Tamil"
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi"
    lowered = text.lower()
    if any(w in lowered for w in ("hola", "pedido", "reembolso", "contraseña", "zapatos", "ayer", "devolver")):
        return "Spanish"
    if any(w in lowered for w in ("bonjour", "commande", "remboursement", "mot de passe", "livraison")):
        return "French"
    return "English"


MULTILINGUAL_GLOSSARY = {
    "கடவுச்சொல்": "forgot password login account reset",
    "உள்நுழைய": "login sign in account password",
    "ஆர்டர்": "order delivery shipping tracking late",
    "பணம்": "refund return money back payment billing",
    "காலணி": "return shoes refund policy",
    "உடைந்த": "broken damaged defective replacement",
    "pedido": "where is my order shipping delivery late",
    "reembolso": "return refund policy money back",
    "zapatos": "return shoes refund",
    "contraseña": "forgot password login account reset",
    "पासवर्ड": "forgot password login account reset",
    "ऑर्डर": "where is my order shipping delivery late",
    "रिफंड": "return refund policy money back",
}


def expand_multilingual_query(text: str) -> str:
    extra = [eng for token, eng in MULTILINGUAL_GLOSSARY.items() if token in text.lower()]
    return f"{text} {' '.join(extra)}".strip()

"""Reusable UI helper renderers for NexaCart Support Desk."""
import html
import streamlit as st
from .pipeline import AGENTS

# Populated by app.py with live Streamlit output placeholders.
OUT_SLOTS: dict = {}

ACCENT = {"query_agent": "#4F46E5", "knowledge_agent": "#3B82F6", "resolution_agent": "#DB2777", "qa_agent": "#8B5CF6", "log_agent": "#0EA5E9"}
ICON = {"query_agent": "①", "knowledge_agent": "②", "resolution_agent": "③", "qa_agent": "④", "log_agent": "⑤"}

def esc(value) -> str:
    return html.escape(str(value or ""))


def panel_h(title: str, sub: str = "") -> str:
    small = f"<small>{esc(sub)}</small>" if sub else ""
    return f"<div class='panel-h'><span class='bar'></span>{esc(title)}{small}</div>"


def render_step(slot, step: dict) -> None:
    """Compact horizontal agent card goes in `slot`; the agent's detailed output goes in its OUT_SLOTS tab."""
    key, status = step["key"], step.get("status", "waiting")
    name, role = AGENTS[key]
    order = list(AGENTS).index(key) + 1
    is_last = order == len(AGENTS)
    timing = f" · {step['duration_s']}s" if step.get("duration_s") is not None else ""
    with slot.container():
        st.markdown(
            f"<div class='agent-card {status}' style='--a:{ACCENT[key]}'>"
            f"<div class='ac-top'><div class='ac-num'>{ICON[key]}</div>"
            f"<div class='ac-step'>{'FINAL STEP' if is_last else f'STEP {order} →'}</div></div>"
            f"<div class='ac-title'>{name}</div><div class='ac-role'>{role}</div>"
            f"<div class='s s-{status}'>{status.upper()}{timing}</div></div>",
            unsafe_allow_html=True,
        )

    out_slot = OUT_SLOTS.get(key)
    if out_slot is not None:
        with out_slot.container():
            out = step.get("output")
            if out:
                render_output(key, out)
                if step.get("error"):
                    st.warning(f"Fell back to rules after: {step['error']}")
            else:
                st.caption(f"{name} has not produced output yet — it will appear here when this step runs.")


def render_output(key: str, out: dict) -> None:
    if key == "query_agent":
        chips = [out["category"], f"Urgency: {out['urgency']}", f"Sentiment: {out['sentiment']}"]
        chips += [f"⚠ {f}" for f in out["risk_flags"]] + ([f"Order {out['order_id']}"] if out["order_id"] else [])
        st.markdown("<div class='chips'>" + "".join(f"<span>{esc(c)}</span>" for c in chips) + "</div>",
                    unsafe_allow_html=True)
        st.caption(f"Summary: {out['summary']}  \nSearch keywords: {out['search_query']}")
    elif key == "knowledge_agent":
        st.caption(f"Searches: {', '.join(out['searches']) or '—'} · {out['reasoning']}")
        if not out["passages"]:
            st.error("No matching document found in the knowledge base.")
        for p in out["passages"]:
            st.markdown(f"<div class='passage'><b>{esc(p['id'])}</b> · {esc(p['section'])}<br>{esc(p['text'])}</div>",
                        unsafe_allow_html=True)
    elif key == "resolution_agent":
        st.progress(out["confidence"], text=f"Confidence {out['confidence']:.0%}")
        st.caption(f"Cited: {', '.join(out['cited_passages']) or 'none'}" + (f" · Gaps: {out['gaps']}" if out["gaps"] else ""))
    else:
        st.json(out)


def render_empty_chat(working: bool = False) -> str:
    if working:
        return ("<div class='chat'><div class='chat-empty working'><div class='big'>⏳</div>"
                "<b>Agents are working on the ticket…</b>"
                "<span>Watch the pipeline above — the drafted reply will appear here as soon as the Log Agent finishes.</span>"
                "</div></div>")
    return ("<div class='chat'><div class='chat-empty'><div class='big'>💬</div>"
            "<b>No conversation yet</b>"
            "<span>Submit a complaint to generate an AI-drafted customer response.</span></div></div>")


def render_result(result: dict) -> None:
    ok = result["status"] == "Resolved"
    cls = "ok" if ok else "esc"
    ctx = st.session_state.get("submitted_ctx") or {}
    cust_name = (ctx.get("customer_name") or "").strip() or "Customer"
    initial = esc(cust_name[:1].upper() or "C")
    order_bit = f" · {esc(ctx['order_id'])}" if ctx.get("order_id") else ""

    customer_bubble = ""
    if ctx.get("complaint"):
        customer_bubble = (
            f"<div class='msg cu'><div class='avatar cu'>{initial}</div>"
            f"<div class='bubble'><div class='who'>{esc(cust_name)}{order_bit}</div>"
            f"{esc(ctx['complaint']).replace(chr(10), '<br>')}</div></div>"
        )

    pct = max(0, min(100, int(round(float(result["confidence"]) * 100))))
    reason = "" if ok else f"<div class='reason'><b>Escalation reason:</b> {esc(result['escalation_reason'])}</div>"
    sources = "".join(f"<span class='src'>{esc(s)}</span>" for s in result["kb_sources"]) or "none"

    st.markdown(
        f"<div class='chat {cls}'>"
        f"<div class='chat-head'><div class='chat-who'><div class='avatar ai'>🤖</div>"
        f"<div><b>NexaCart AI Support</b><small>{esc(result['ticket_id'])} · {esc(result['category'])}</small></div></div>"
        f"<span class='badge {cls}'>{'✓ RESOLVED' if ok else '⚑ ESCALATED'}</span></div>"
        f"<div class='chat-body'>{customer_bubble}"
        f"<div class='msg ai'><div class='avatar ai'>🤖</div><div class='bubble'><div class='who'>AI-drafted response</div>"
        f"{esc(result['response']).replace(chr(10), '<br>')}</div></div></div>"
        f"<div class='chat-foot'>{reason}"
        f"<div class='conf-row'>Confidence<div class='conf'><i style='width:{pct}%'></i></div>{pct}%</div>"
        f"<div class='src-row'><b>Sources:</b> {sources}</div></div></div>",
        unsafe_allow_html=True,
    )




"""NexaCart Support Desk — Streamlit UI for the AutoGen multi-agent customer support pipeline.

Run:  streamlit run app.py
"""
from __future__ import annotations

import asyncio
import html
import json
from pathlib import Path

import pandas as pd

import streamlit as st

from support_desk.config import KB_DIR, SAMPLES_FILE, get_settings
from support_desk.knowledge_base import get_kb
from support_desk.evaluation import evaluate_retrieval
from support_desk.pipeline import AGENTS, SupportPipeline
from support_desk.ticket_log import HumanReviewStore, TicketLogger

st.set_page_config(page_title="NexaCart Support Desk", page_icon="🛒", layout="wide")

SETTINGS = get_settings()
LOGGER = TicketLogger()
REVIEW_STORE = HumanReviewStore()
SAMPLES = json.loads(SAMPLES_FILE.read_text(encoding="utf-8"))
# Indigo / lotus / light-blue family
ACCENT = {"query_agent": "#4F46E5", "knowledge_agent": "#3B82F6", "resolution_agent": "#DB2777", "qa_agent": "#8B5CF6", "log_agent": "#0EA5E9"}
ICON = {"query_agent": "①", "knowledge_agent": "②", "resolution_agent": "③", "qa_agent": "④", "log_agent": "⑤"}

# Output placeholders (one per agent) – filled live by render_step(), rebuilt on every script run.
OUT_SLOTS: dict = {}

# ---------------------------------------------------------------------------- theme
from support_desk.ui_styles import inject_styles
inject_styles()

from support_desk import ui_tabs
from support_desk.ui_tabs import esc, panel_h, render_step, render_output, render_empty_chat, render_result

# Share the live output placeholders with the UI renderer module.
ui_tabs.OUT_SLOTS = OUT_SLOTS

# ---------------------------------------------------------------------------- header
mode_label = f"AutoGen · {SETTINGS.model}" if SETTINGS.llm_enabled else "Offline demo mode (no API key)"
mode_color = "#22C55E" if SETTINGS.llm_enabled else "#FBBF24"
st.markdown(
    f"<div class='hero'><div><div class='kicker'>NexaCart · AI Customer Support Desk</div>"
    "<h3>Every complaint, answered from policy.</h3>"
    "<p>Five AutoGen agents read the complaint, retrieve the company's own policy passages, validate the grounded "
    "reply and log the ticket — escalating anything risky to a human.</p></div>"
    f"<span class='pill'><span class='dot' style='background:{mode_color}'></span>{esc(mode_label)}</span></div>",
    unsafe_allow_html=True,
)

log_df = LOGGER.read()
total = len(log_df)
resolved = int((log_df["status"] == "Resolved").sum()) if total else 0
escalated = total - resolved
avg_conf = log_df["confidence"].astype(float).mean() if total else 0.0
review_df = REVIEW_STORE.read()
pending_reviews = int((review_df["review_status"] == "Pending").sum()) if not review_df.empty else 0
for col, (value, label, accent, icon) in zip(
    st.columns(5),
    [(total, "Tickets logged", "#4F46E5", "🎫"), (resolved, "Auto-resolved", "#059669", "✓"),
     (escalated, "Escalated", "#DB2777", "⚑"), (pending_reviews, "Pending human review", "#8B5CF6", "👤"),
     (f"{avg_conf:.0%}", "Avg. confidence", "#0EA5E9", "◎")],
):
    col.markdown(
        f"<div class='stat' style='--a:{accent}'><div><div class='v'>{value}</div><div class='l'>{label}</div></div>"
        f"<div class='ic'>{icon}</div></div>",
        unsafe_allow_html=True,
    )
st.write("")

desk, log_tab, review_tab, kb_tab, eval_tab, about_tab = st.tabs(["Support Desk", "Ticket Log", "Human Review", "Knowledge Base", "RAG Evaluation", "How it works"])

# ------------------------------------------------------------------------ desk tab

def load_sample():
    label = st.session_state.get("sample_pick", "")
    sample = next(
        (s for s in SAMPLES if s.get("label") == label),
        None,
    )

    if sample:
        st.session_state["complaint"] = sample.get("text", "")
        st.session_state["customer_name"] = sample.get("customer_name", "")
        st.session_state["order_id"] = sample.get("order_id", "")

            
with desk:
    # Layout skeleton (visual order): pipeline strip → complaint | chat window → agent activity.
    # Containers are created first so each can be filled in whatever order the logic needs.
    pipe_area = st.container()
    left, right = st.columns(2, gap="large")
    insight_area = st.container()

    # LEFT: Customer complaint intake
    with left:
        st.markdown(panel_h("New complaint", "type your own or pick a sample"), unsafe_allow_html=True)

        st.pills(
            "Try a sample complaint",
            [s["label"] for s in SAMPLES],
            key="sample_pick",
            on_change=load_sample,
        )

        with st.form("intake"):
            c1, c2 = st.columns(2)
            c1.text_input("Customer name", key="customer_name", placeholder="Optional")
            c2.text_input("Order ID", key="order_id", placeholder="e.g. ORD-48213")

            st.text_area(
                "Complaint",
                key="complaint",
                height=170,
                max_chars=2000,
                placeholder="Describe the problem in the customer's own words…",
            )

            submitted = st.form_submit_button(
                "Run AI support pipeline →",
                width="stretch",
            )

    # RIGHT: Chat window with the AI-drafted customer response
    with right:
        st.markdown(panel_h("Customer conversation", "AI-drafted response"), unsafe_allow_html=True)
        result_slot = st.empty()

    # BOTTOM: per-agent detailed output, one tab per agent (filled live by render_step)
    with insight_area:
        st.markdown(panel_h("Agent activity", "open a tab to inspect what each agent produced"), unsafe_allow_html=True)
        out_tabs = st.tabs([f"{ICON[k]} {AGENTS[k][0]}" for k in AGENTS])
        for tab, k in zip(out_tabs, AGENTS):
            with tab:
                OUT_SLOTS[k] = st.empty()

    # TOP: Agent pipeline – five agent cards side by side
    with pipe_area:
        st.markdown(panel_h("Agent pipeline", "Query → Knowledge → Resolution → QA → Log"), unsafe_allow_html=True)

        agent_cols = st.columns(len(AGENTS), gap="small")
        slots = {key: col.empty() for key, col in zip(AGENTS, agent_cols)}

        if submitted and not st.session_state.get("complaint", "").strip():
            st.warning("Please enter a complaint first.")
            submitted = False

        if submitted:
            for key in AGENTS:
                render_step(slots[key], {"key": key, "status": "waiting"})

            result_slot.markdown(render_empty_chat(working=True), unsafe_allow_html=True)

            with st.spinner("Agents are working on the ticket…"):
                st.session_state.result = asyncio.run(
                    SupportPipeline(SETTINGS, LOGGER).run(
                        st.session_state.complaint,
                        st.session_state.customer_name,
                        st.session_state.order_id,
                        on_step=lambda step: render_step(slots[step["key"]], step),
                    )
                )

            # UI only: remember what was submitted so the chat window can show the customer's message
            st.session_state.submitted_ctx = {
                "complaint": st.session_state.complaint,
                "customer_name": st.session_state.customer_name,
                "order_id": st.session_state.order_id,
            }

            st.rerun()

        result = st.session_state.get("result")
        steps = {s["key"]: s for s in result["steps"]} if result else {}

        for key in AGENTS:
            render_step(
                slots[key],
                steps.get(key, {"key": key, "status": "waiting"}),
            )

    with result_slot.container():
        if result:
            render_result(result)
        else:
            st.markdown(render_empty_chat(), unsafe_allow_html=True)


# ------------------------------------------------------------------------- log tab
with log_tab:
    if log_df.empty:
        st.info("No tickets yet — the log file is created with the first ticket.")
    else:
        f1, f2, f3 = st.columns([2, 2, 3])
        status_f = f1.multiselect("Status", ["Resolved", "Escalated"])
        urgency_f = f2.multiselect("Urgency", ["High", "Medium", "Low"])
        query = f3.text_input("Search", placeholder="ticket id, customer, complaint…")
        view = log_df.iloc[::-1]
        if status_f:
            view = view[view["status"].isin(status_f)]
        if urgency_f:
            view = view[view["urgency"].isin(urgency_f)]
        if query:
            view = view[view.apply(lambda r: query.lower() in " ".join(r.astype(str)).lower(), axis=1)]
        styled = view.style.map(
            lambda v: "background-color:#DCFCE7;color:#15803D;font-weight:700" if v == "Resolved"
            else "background-color:#FEE2E2;color:#B91C1C;font-weight:700" if v == "Escalated" else "",
            subset=["status"],
        )
        st.dataframe(styled, width="stretch", hide_index=True, height=min(440, 38 + 35 * len(view)))
        d1, d2, d3, _ = st.columns([1, 1, 1, 3])
        d1.download_button("⬇ CSV", view.to_csv(index=False), "ticket_log.csv", "text/csv", width="stretch")
        d2.download_button("⬇ Excel", TicketLogger.to_excel_bytes(view), "ticket_log.xlsx", width="stretch")
        if LOGGER.txt_path.exists():
            d3.download_button("⬇ TXT", LOGGER.txt_path.read_text(encoding="utf-8"), "ticket_log.txt", width="stretch")

# -------------------------------------------------------------------- human review tab
with review_tab:
    st.markdown("#### Human-in-the-loop review queue")
    st.caption("Escalated AI tickets are queued for a support employee to review, edit, approve, or mark handled. "
               "This demo records approval locally; it does not send messages to customers.")
    review_df = REVIEW_STORE.read()
    if review_df.empty:
        st.info("No escalated tickets are waiting yet. Run a high-risk or unsupported complaint to create a review item.")
    else:
        r1, r2 = st.columns(2)
        status_filter = r1.multiselect("Review status", ["Pending", "Approved", "Resolved by human"],
                                     default=["Pending"], key="review_status_filter")
        search_review = r2.text_input("Find a ticket", placeholder="ticket ID, customer, order…", key="review_search")
        view_review = review_df.iloc[::-1]
        if status_filter:
            view_review = view_review[view_review["review_status"].isin(status_filter)]
        if search_review.strip():
            term = search_review.lower().strip()
            view_review = view_review[view_review.apply(lambda row: term in " ".join(row.astype(str)).lower(), axis=1)]
        st.dataframe(view_review[["ticket_id", "timestamp", "customer_name", "category", "urgency",
                                  "review_status", "escalation_reason"]], width="stretch", hide_index=True)
        pending_ids = review_df.loc[review_df["review_status"] == "Pending", "ticket_id"].astype(str).tolist()
        if pending_ids:
            selected_id = st.selectbox("Select pending ticket", pending_ids, key="review_ticket_select")
            selected = review_df[review_df["ticket_id"].astype(str) == selected_id].iloc[0]
            st.markdown(f"**{esc(selected['ticket_id'])} · {esc(selected['category'])} · {esc(selected['urgency'])} urgency**")
            st.markdown("**Customer complaint**")
            st.info(str(selected["complaint"]))
            st.markdown("**AI-proposed response**")
            st.write(str(selected["original_response"]))
            reviewer = st.text_input("Reviewer name", value="Support Agent", key=f"reviewer_{selected_id}")
            edited = st.text_area("Review / edit the response", value=str(selected["approved_response"]),
                                 height=180, key=f"review_response_{selected_id}")
            notes = st.text_area("Internal review notes (optional)", key=f"review_notes_{selected_id}", height=80)
            a1, a2 = st.columns(2)
            if a1.button("✓ Approve for customer delivery", type="primary", key=f"approve_{selected_id}"):
                REVIEW_STORE.update(selected_id, review_status="Approved", reviewer=reviewer,
                                   review_notes=notes, approved_response=edited)
                st.success("Response approved and saved to the local review log. No email was sent.")
                st.rerun()
            if a2.button("Mark handled by human", key=f"resolve_human_{selected_id}"):
                REVIEW_STORE.update(selected_id, review_status="Resolved by human", reviewer=reviewer,
                                   review_notes=notes, approved_response=edited)
                st.success("Ticket marked as handled by a human reviewer.")
                st.rerun()
        else:
            st.success("No pending review items. Use the status filter to inspect completed reviews.")

# -------------------------------------------------------------------------- kb tab
with kb_tab:
    kb = get_kb()
    info = kb.retrieval_info
    st.caption(f"{info['documents']} documents · {info['passages']} searchable passages · "
               f"Hybrid BM25 + Dense retrieval · backend: {info['dense_backend']} · "
               f"FAISS: {'active' if info['faiss_available'] else 'fallback mode'}")

    with st.expander("＋ Add policy PDF to the knowledge base", expanded=False):
        uploads = st.file_uploader("Upload one or more policy / FAQ PDFs", type=["pdf"],
                                  accept_multiple_files=True, key="kb_pdf_upload")
        if st.button("Import PDF documents", disabled=not uploads, key="import_kb_pdfs"):
            KB_DIR.mkdir(parents=True, exist_ok=True)
            saved, skipped = [], []
            for upload in uploads or []:
                safe_name = Path(upload.name).name
                if not safe_name.lower().endswith(".pdf"):
                    skipped.append(safe_name)
                    continue
                target = KB_DIR / safe_name
                if target.exists():
                    skipped.append(f"{safe_name} (already exists)")
                    continue
                target.write_bytes(upload.getvalue())
                saved.append(safe_name)
            get_kb.cache_clear()
            if saved:
                st.success("Imported: " + ", ".join(saved))
            if skipped:
                st.info("Skipped: " + ", ".join(skipped))
            st.rerun()

    st.markdown("#### Search policy evidence")
    rag_query = st.text_input("Test a customer question against the indexed policies",
                              placeholder="e.g. I was charged twice for the same order", key="rag_search_query")
    if st.button("Search knowledge base", key="rag_search_btn", disabled=not rag_query.strip()):
        results = kb.search(rag_query.strip(), top_k=5)
        if not results:
            st.warning("No relevant evidence found. The system should abstain and escalate.")
        else:
            for passage, score in results:
                page_label = f" · page {passage.page}" if passage.page else ""
                st.markdown(f"<div class='passage'><b>{esc(passage.source)} · {esc(passage.section)}{esc(page_label)} · score {score:.4f}</b><br>{esc(passage.text).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    st.markdown("#### Indexed source documents")
    for doc in kb.documents():
        with st.expander(f"📄 {doc['name']}"):
            if doc["name"].lower().endswith(".pdf"):
                pdf_path = KB_DIR / doc["name"]
                st.caption("PDF indexed with page-level provenance.")
                st.download_button("Download source PDF", pdf_path.read_bytes(), file_name=doc["name"],
                                  mime="application/pdf", key=f"download_{doc['name']}")
            else:
                st.markdown(doc["content"])

# ---------------------------------------------------------------------- evaluation tab
with eval_tab:
    st.markdown("#### Retrieval quality benchmark")
    st.caption("Runs the local, repeatable test set against the current knowledge base. No LLM call is needed.")
    benchmark = evaluate_retrieval(get_kb(), top_k=3)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Hit @ 1", f"{benchmark['hit_at_1']:.0%}")
    m2.metric("Hit @ 3", f"{benchmark['hit_at_k']:.0%}")
    m3.metric("Mean Reciprocal Rank", f"{benchmark['mrr']:.2f}")
    m4.metric("No-match accuracy", f"{benchmark['no_match_accuracy']:.0%}")
    st.caption(f"{benchmark['cases']} test queries · {benchmark['positive_cases']} answerable · {benchmark['no_match_cases']} expected abstentions")
    st.dataframe(benchmark["rows"], width="stretch", hide_index=True)
    st.download_button("Download benchmark results (CSV)",
                      pd.DataFrame(benchmark["rows"]).to_csv(index=False),
                      "rag_evaluation_results.csv", "text/csv")

# ----------------------------------------------------------------------- about tab
with about_tab:
    st.markdown(
        f"""
**Workflow** — `Customer Query Agent → Knowledge Base Agent → Resolution Agent → QA / Critic Agent → Log Agent` (strict order, one
AutoGen turn per agent, {SETTINGS.agent_timeout_s}s timeout each, so every run terminates cleanly).

| Agent | Responsibility | Tools |
|---|---|---|
| Customer Query Agent | category, urgency, sentiment, risk flags, search keywords | – |
| Knowledge Base Agent | retrieves only relevant passages (verbatim, with ids) | `search_knowledge_base` |
| Resolution Agent | polite reply grounded only in retrieved passages + confidence | – |
| QA / Critic Agent | checks grounding, citations, and unsupported claims | – |
| Log Agent | applies the escalation policy, writes CSV/TXT log | `record_ticket` |

**Escalation rule** — escalate when urgency is High, the customer is very angry, no matching document was found,
the complaint involves a legal threat / fraud / payment dispute, or confidence < {SETTINGS.confidence_threshold:.0%}.
A deterministic guardrail re-checks the Log Agent's decision; it can only make the outcome stricter.
"""
    )

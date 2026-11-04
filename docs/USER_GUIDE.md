# NexaCart Support Desk — User Guide

## 1. Overview

NexaCart is a Streamlit-based AI customer support desk. A user submits a complaint, the AutoGen-powered agent pipeline analyzes it, searches company policies, drafts and checks a response, and either resolves or escalates the ticket.

## 2. Launch the Application

### Windows CMD

```cmd
.venv\Scripts\activate.bat
python -m streamlit run app.py
```

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

### Linux / macOS

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).

## 3. Submit a Complaint

1. Open the **Support Desk** tab.
2. Select a sample complaint or enter a custom complaint.
3. Optionally enter the customer name and order ID.
4. Click **Run AI support pipeline**.
5. Observe the sequential agent pipeline as it processes the complaint.
6. Review the drafted response, detected category, confidence, source documents, and final status.

## 4. Understand the Result

### Resolved

A ticket may be resolved when relevant policy evidence is retrieved, the response is grounded, QA passes, and no mandatory escalation condition applies.

### Escalated

A ticket is escalated when it is risky, uncertain, unsupported by the knowledge base, or fails quality checks. Escalation prevents the system from inventing policy details or making unsupported commitments.

## 5. Agent Pipeline

The application uses five AutoGen agents in a sequential workflow:

1. **Customer Query Agent** — analyzes category, urgency, sentiment, language, and risk.
2. **Knowledge Base Agent** — retrieves relevant policy passages.
3. **Resolution Agent** — drafts a response using retrieved evidence.
4. **Quality Assurance Agent** — validates grounding, citations, and response quality.
5. **Log Agent** — proposes status and records the ticket.

The pipeline includes retrieval, validation, escalation, and human-review safeguards.

## 6. Explore Other Tabs

- **Ticket Log:** Review, filter, and download recorded tickets.
- **Human Review:** Inspect escalated tickets, edit responses, approve them for customer delivery, or mark tickets as handled by a human.
- **Knowledge Base:** Inspect policy documents and use the supported upload/reload workflow.
- **RAG Evaluation:** Run the bundled retrieval benchmark and review metrics.
- **How it works:** Review the workflow explanation.

## 7. Sample Complaint Scenarios

Samples cover delayed shipment, return/refund, forgotten password, damaged product, duplicate/triple charge, corporate gift-card inquiry, wrong-size item, missing reset email, unknown charge/suspected fraud, and lost parcel with an angry customer.

## 8. Multilingual Use

Submit a complaint in the customer's language. Validated examples include English, Tamil, Hindi, and Spanish. The application attempts to detect language and respond in the same language. Detection and generation may not be perfect for every dialect or mixed-language complaint.

## 9. Ticket Records

Ticket records are stored under `logs/`. Ticket Log supports inspection and download. Escalated cases can also appear in the Human Review workflow.

## 10. Troubleshooting

| Issue | Suggested action |
|---|---|
| App does not start | Activate `.venv`, install `requirements.txt`, and verify Python version |
| Missing API configuration | Check `.env` against `.env.example`; keep the key private |
| Agent returns fallback output | Check API key, model configuration, network, and application logs |
| Knowledge source not found | Verify `knowledge_base/` and inspect retrieval/evaluation |
| Sample button does not populate | Restart Streamlit and verify sample data keys |
| Port 8501 is busy | Stop another Streamlit process or use another port |
| Tests fail | Run `python -m pytest -v` and inspect the first failing traceback |

## 11. Security Reminder

Do not use real customer PII or sensitive production information in this demo. Protect `.env`, API credentials, ticket logs, and customer data.

This is a Buildathon prototype, not a certified production support system.
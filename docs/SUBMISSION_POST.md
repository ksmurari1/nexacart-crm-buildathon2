# NexaCart Support Desk — Buildathon 2.0 Submission

## Skool / Community Post

### 🛒 NexaCart Support Desk | AI Customer Support Automation with 5 AutoGen Agents

Hi everyone! I'm sharing my **NexaCart AI Customer Support Desk**, built for the Social Eagle AI Buildathon 2.0.

### 💡 What it does
A customer submits a complaint through a Streamlit interface. Five specialized AutoGen agents collaborate to analyze the request, retrieve relevant company policy, draft a grounded response, validate quality, and record the ticket.

### 🤖 The 5-agent workflow
1. **Customer Query Agent** — identifies category, urgency, sentiment, language, and risk.
2. **Knowledge Base Agent** — retrieves relevant policy passages through the RAG pipeline.
3. **Resolution Agent** — drafts a polite response grounded in retrieved evidence.
4. **Quality Assurance Agent** — validates grounding, citations, and response quality.
5. **Log Agent** — proposes ticket status and records the case.

### 🛡️ Key features
- Policy-grounded RAG with FAISS and hybrid retrieval
- Pydantic validation for structured agent outputs
- QA / critic agent
- Deterministic escalation guardrails
- Human-review workflow for risky or unsupported cases
- Ticket logging and downloadable records
- Multilingual complaint handling (validated in English, Tamil, Hindi, and Spanish)
- Streamlit dashboard with Agent Pipeline, Ticket Log, Human Review, Knowledge Base, and RAG Evaluation

### 🧪 Testing highlights
- 6 mandatory scenarios covered
- 2 additional custom scenarios covered
- 10 Pydantic model tests passed
- 23 integrated tests passed
- Retrieval benchmark evaluated on a small bundled dataset

### 📸 Screenshots
- Application dashboard
- Resolved customer complaint
- Escalated customer complaint
- Ticket Log
- System architecture and workflow

### 🔗 GitHub Repository
[Add your repository URL here]

### 🧰 Technology Stack
Python · Microsoft AutoGen · Streamlit · OpenAI · RAG · FAISS · Pydantic · Pytest

This project helped me explore how specialized agents, retrieval grounding, validation, and human-in-the-loop guardrails can work together in a practical customer-support workflow.

Feedback and suggestions are welcome! 🙌

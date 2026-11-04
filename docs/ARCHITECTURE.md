# NexaCart Support Desk — Architecture

## Overview
NexaCart is a policy-grounded AI customer support application built with Streamlit and Microsoft AutoGen. Five specialized agents collaborate in a controlled pipeline to analyze complaints, retrieve company knowledge, draft responses, validate quality, and log outcomes.

## High-Level Architecture
```mermaid
flowchart TB
    C[Customer] --> UI[Streamlit Application]
    UI --> P[Support Pipeline / AutoGen Team]
    P --> Q[1. Customer Query Agent]
    Q --> K[2. Knowledge Base Agent]
    K --> R[3. Resolution Agent]
    R --> QA[4. Quality Assurance Agent]
    QA --> L[5. Log Agent]
    KB[Company Knowledge Base<br/>PDF / Markdown] --> ING[Document Ingestion & Chunking]
    ING --> EMB[Embeddings]
    EMB --> VS[FAISS Vector Store]
    K <--> VS
    L --> G[Python Escalation Guardrails]
    G --> TL[Ticket Logs]
    G --> HR[Human Review Queue]
    P --> UI
    TL --> UI
    HR --> UI
```

## Agent Execution Sequence
```mermaid
sequenceDiagram
    participant U as Streamlit UI
    participant P as Support Pipeline
    participant Q as Customer Query Agent
    participant K as Knowledge Base Agent
    participant R as Resolution Agent
    participant A as QA Agent
    participant L as Log Agent
    participant G as Python Guardrails
    participant T as Ticket Log / Human Review
    U->>P: Complaint, customer name, order ID
    P->>Q: Analyze complaint
    Q-->>P: Category, urgency, sentiment, language, risk flags
    P->>K: Retrieve relevant policy evidence
    K-->>P: Passage IDs and retrieval result
    P->>P: Validate passage IDs and load exact source text
    P->>R: Complaint + analysis + evidence
    R-->>P: Draft response, confidence, citations, gaps
    P->>A: Validate response against evidence
    A-->>P: QA result, issues, quality score
    P->>L: Complaint context, evidence, response, QA result
    L-->>P: Status proposal, escalation reason, ticket record
    P->>G: Apply deterministic escalation rules
    G->>T: Persist ticket and human-review record if needed
    P-->>U: Response, status, confidence, source, pipeline trace
```

## Agent Responsibilities
| Agent | Responsibility | Typical output |
|---|---|---|
| Customer Query Agent | Understand and classify the complaint | Category, urgency, sentiment, language, risk flags, summary, search query |
| Knowledge Base Agent | Find relevant company policy evidence | Passage IDs, retrieval status, search rationale |
| Resolution Agent | Draft an empathetic response grounded in retrieved evidence | Reply, confidence, citations, knowledge gaps |
| Quality Assurance Agent | Check grounding, citations, coverage, and response quality | Pass/fail, issues, score, valid citations |
| Log Agent | Propose disposition and record the case | Status proposal, escalation reason, ticket details |

## Retrieval Architecture
```mermaid
flowchart TD
    A[Policy PDF / Markdown / TXT] --> B[Text extraction]
    B --> C[Section-aware chunking]
    C --> D[Passage metadata: source, page, section]
    D --> E[Keyword ranking / BM25]
    D --> F[Dense vector representation]
    F --> G{Dense backend}
    G --> H[FAISS inner-product index]
    G --> I[NumPy / scikit-learn fallback]
    E --> J[Relevance-gated ranking fusion]
    H --> J
    I --> J
    J --> K[Top evidence passages: stable IDs]
    K --> L[Resolution Agent]
    L --> M[QA Agent]
    M --> N{Evidence and citations valid?}
    N -->|Yes| O[Log Agent + guardrails]
    N -->|No| P[Escalation]
    O --> P
```

## Escalation Guardrails
The deterministic Python guardrail can make a proposed outcome stricter; it must not override a mandatory escalation with an automatic resolution.

Escalation conditions include:
- High urgency
- Very angry customer sentiment
- Legal threat, fraud, or payment dispute
- No relevant knowledge passage
- Low resolution confidence
- QA verification failure
- Agent error, timeout, or incomplete processing

## Logging and Human Review
Ticket activity is persisted under `logs/`. The application supports ticket-log inspection and a human-review workflow for escalated cases. Human-review records can track pending review and approval/edit outcomes.

## Design Principles
- **Grounded generation:** policy details must come from retrieved source passages.
- **Separation of concerns:** each agent has a narrowly defined responsibility.
- **Defense in depth:** model decisions are checked by QA and deterministic Python rules.
- **Safe failure:** missing evidence or processing errors result in escalation rather than fabricated policy.
- **Traceability:** retain classification, source evidence, response, QA outcome, status, and ticket record.
- **Human oversight:** sensitive or uncertain cases are routed to a person.

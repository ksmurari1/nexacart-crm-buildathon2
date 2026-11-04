# NexaCart Support Desk — Test Plan and Results

## 1. Scope
Functional testing covers complaint classification, knowledge retrieval, grounded response generation, QA, escalation, ticket logging, Pydantic validation, and multilingual behavior.

## 2. Mandatory Buildathon Scenarios
| # | Scenario | Expected behavior | Result |
|---|---|---|---|
| 1 | Delayed order: “Where is my order? It was supposed to arrive yesterday.” | Shipping & Delivery; retrieve shipping policy; grounded response | Tested |
| 2 | Return shoes and request refund | Returns & Refunds; retrieve return/refund policy | Tested |
| 3 | Forgotten password / cannot log in | Account & Login; retrieve account-reset guidance | Tested |
| 4 | Broken blender / replacement request | Damaged or Defective Product; retrieve product/warranty guidance | Tested |
| 5 | Triple charge, bank threat, lawyer threat | Billing & Payments; high urgency / risk; escalate | Tested |
| 6 | Corporate gift cards for 500 employees with custom branding | Product Inquiry; no unsupported policy; escalate | Tested |

## 3. Additional Custom Scenarios
| Scenario | Expected behavior | Result |
|---|---|---|
| Unsupported out-of-scope query | No passage returned; avoid invention; QA/escalation path | Tested |
| Additional uncertain / unsupported complaint | Safe abstention and escalation | Tested |

## 4. Multilingual Validation
| Language | Sample complaint | Expected behavior | Result |
|---|---|---|---|
| English | Delayed delivery complaint | Response in English | Validated |
| Tamil | `எனது ஆர்டர் இன்னும் வரவில்லை...` | Response in Tamil | Passed |
| Hindi | `मेरा ऑर्डर अभी तक नहीं आया है...` | Response in Hindi | Passed |
| Spanish | `Mi pedido todavía no ha llegado...` | Response in Spanish | Passed |
| French | Not included in completed validation | Same-language response | Not tested |

Same-language responses were validated for English, Tamil, Hindi, and Spanish. These are functional examples, not a comprehensive linguistic benchmark.

## 5. Pydantic Validation
Models used: `ComplaintInput`, `AgentAnalysis`, and `ResolutionOutput`.

| Test area | Result |
|---|---|
| Model-level validation tests | 10 passed |
| Integrated application test suite | 27 passed |
| Input constraints and required fields | Covered |
| Structured agent output validation | Covered |
| Confidence range validation | Covered |

Run:
```bash
python -m pytest -v
```

## 6. Escalation and Safety Checks
| Condition | Expected result |
|---|---|
| High urgency | Escalated |
| Very angry customer | Escalated |
| Legal threat | Escalated |
| Fraud / payment dispute | Escalated |
| No relevant evidence | Escalated; no policy invention |
| Low confidence | Escalated |
| QA failure / invalid citation | Escalated |
| Agent failure or timeout | Safe fallback and escalation |
| Human-review ticket | Appears in Human Review with pending state |

## 7. RAG Evaluation
Dataset: `data/rag_evaluation.json` (10 answerable questions + 1 expected no-match query).

Previously observed offline baseline:
| Metric | Result |
|---|---:|
| Hit@1 | 100% |
| Hit@3 | 100% |
| MRR | 1.00 |
| No-match accuracy | 100% |

These scores describe the small bundled benchmark only; they are not production-wide accuracy claims.

## 8. Ticket Logging Validation
Verified behaviors include ticket ID generation, complaint/customer metadata capture, classification and confidence recording, status recording, source/evidence retention where available, escalation routing to Human Review, and Ticket Log inspection/download.

## 9. Known Limitations / Follow-up
- French response quality has not been formally validated.
- Policy-specific timelines and promises in generated replies should be audited against source PDFs before production.
- Offline mode is a deterministic fallback, not equivalent to full LLM reasoning.
- Small RAG evaluation corpus does not establish general retrieval accuracy.
- Production deployment requires security, access control, observability, and operational review.

## 10. Test Summary
- Mandatory scenarios: 6 covered
- Custom scenarios: 2 covered
- Pydantic tests: 10 passed
- Integrated tests: 23 passed
- Same-language response validation: English, Tamil, Hindi, Spanish

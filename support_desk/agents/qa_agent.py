"""Agent 5 — Quality Assurance: validates citations and evidence coverage before delivery."""
from autogen_agentchat.agents import AssistantAgent
SYSTEM_MESSAGE = """You are NexaCart's QA / Critic Agent. Audit the proposed response against supplied policy passages.
Check: (1) every policy claim is supported, (2) citations refer to provided passage IDs,
(3) the response addresses the complaint, (4) unsupported promises or invented timelines are absent.
If evidence is missing, mark passed=false and identify gaps. Never rewrite policy or invent facts.
Return ONLY JSON: {"passed": true|false, "grounded": true|false, "valid_citations": ["id"],
"issues": ["..."], "quality_score": 0.0-1.0}"""
def create_qa_agent(model_client):
    return AssistantAgent(name="qa_agent", description="Audits answer grounding and citations.",
                         model_client=model_client, system_message=SYSTEM_MESSAGE)

# NexaCart memory integration guide (apply manually to pipeline.py)

## A. Import near the top of support_desk/pipeline.py
from .memory import find_memory, format_memory_context, remember_ticket

## B. At the beginning of run(), after ComplaintInput validation:
memory_records = find_memory(
    customer_name=complaint.customer_name,
    order_id=complaint.order_id,
)
memory_context = format_memory_context(memory_records)

## C. Add memory_context to the Query Agent's task/input.
# Example:
# query_input = f"{complaint.complaint}\n\n{memory_context}"
# Keep memory explicitly labeled as historical context. It is NOT policy evidence.

## D. After the final ticket dict is constructed and logged:
# remember_ticket({
#     "ticket_id": ticket.get("ticket_id"),
#     "timestamp": ticket.get("timestamp"),
#     "customer_name": complaint.customer_name,
#     "order_id": complaint.order_id,
#     "category": analysis.get("category"),
#     "urgency": analysis.get("urgency"),
#     "sentiment": analysis.get("sentiment"),
#     "status": ticket.get("status"),
#     "summary": analysis.get("summary"),
#     "response": resolution.get("reply"),
#     "escalation_reason": ticket.get("escalation_reason"),
# })

## IMPORTANT
# Do not add memory to KB citations or retrieval scores.
# Persist only after a ticket reaches a final status.
# Review actual variable names/return shapes in pipeline.py before applying.

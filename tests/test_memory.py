from support_desk.memory import (
    find_memory,
    format_memory_context,
    remember_ticket,
)


def test_memory_round_trip(tmp_path, monkeypatch):
    import support_desk.memory as memory

    monkeypatch.setattr(memory, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory, "MEMORY_FILE", tmp_path / "customer_memory.json")

    ticket = {
        "ticket_id": "TKT-100",
        "customer_name": "Carlos Mendes",
        "order_id": "ORD-60277",
        "category": "Shipping & Delivery",
        "urgency": "Medium",
        "sentiment": "Neutral",
        "status": "Escalated",
        "summary": "Order delivery is delayed",
        "resolution_summary": "Customer was advised to check tracking",
        "timestamp": "2026-11-04T10:00:00",
    }

    assert remember_ticket(ticket) == 2
    results = find_memory(customer_name="Carlos Mendes", order_id="ORD-60277")
    assert len(results) == 1
    assert results[0]["ticket_id"] == "TKT-100"
    assert "HISTORICAL CUSTOMER/TICKET CONTEXT" in format_memory_context(results)


def test_order_id_match_takes_precedence(tmp_path, monkeypatch):
    import support_desk.memory as memory

    monkeypatch.setattr(memory, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory, "MEMORY_FILE", tmp_path / "customer_memory.json")

    remember_ticket({
        "ticket_id": "TKT-OLD",
        "customer_name": "Carlos Mendes",
        "order_id": "ORD-OLD",
        "status": "Resolved",
        "summary": "Old order",
    })
    remember_ticket({
        "ticket_id": "TKT-NEW",
        "customer_name": "Carlos Mendes",
        "order_id": "ORD-NEW",
        "status": "Escalated",
        "summary": "New order",
    })

    found = find_memory(customer_name="Carlos Mendes", order_id="ORD-NEW")
    assert [x["ticket_id"] for x in found] == ["TKT-NEW"]


def test_missing_identifiers_do_not_write(tmp_path, monkeypatch):
    import support_desk.memory as memory

    monkeypatch.setattr(memory, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory, "MEMORY_FILE", tmp_path / "customer_memory.json")
    assert remember_ticket({"ticket_id": "TKT-X"}) == 0
    assert not (tmp_path / "customer_memory.json").exists()


def test_corrupt_memory_fails_safely(tmp_path, monkeypatch):
    import support_desk.memory as memory

    monkeypatch.setattr(memory, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory, "MEMORY_FILE", tmp_path / "customer_memory.json")
    (tmp_path / "customer_memory.json").write_text("{broken", encoding="utf-8")
    assert find_memory(order_id="ORD-1") == []

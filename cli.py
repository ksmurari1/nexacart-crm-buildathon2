"""Command-line runner: process one complaint, or every sample complaint with --samples.

    python cli.py "I forgot my password and can't log in." --name "Mei Lin"
    python cli.py --samples
"""
from __future__ import annotations

import argparse
import asyncio
import json

from support_desk.config import SAMPLES_FILE
from support_desk.pipeline import SupportPipeline


def show(step: dict) -> None:
    if step["status"] != "running":
        print(f"  [{step['status'].upper():5}] {step['name']:<22} {step['duration_s']}s")


async def main() -> None:
    parser = argparse.ArgumentParser(description="NexaCart Support Desk CLI")
    parser.add_argument("complaint", nargs="?", help="complaint text")
    parser.add_argument("--name", default="")
    parser.add_argument("--order", default="")
    parser.add_argument("--samples", action="store_true", help="run all sample complaints")
    args = parser.parse_args()
    if args.samples:
        jobs = [(s["text"], s["customer_name"], s["order_id"], s["expected"]) for s in json.loads(SAMPLES_FILE.read_text())]
    elif args.complaint:
        jobs = [(args.complaint, args.name, args.order, None)]
    else:
        parser.error("give a complaint or --samples")
    pipeline = SupportPipeline()
    for text, name, order, expected in jobs:
        print(f"\n> {text}")
        ticket = await pipeline.run(text, name, order, on_step=show)
        check = "" if expected is None else ("  (as expected)" if ticket["status"] == expected else f"  (expected {expected})")
        print(f"  => {ticket['ticket_id']} {ticket['status']}{check} | {ticket['category']} / {ticket['urgency']} / "
              f"{ticket['sentiment']} | sources: {', '.join(ticket['kb_sources']) or 'none'}")
        if ticket["escalation_reason"]:
            print(f"     reason: {ticket['escalation_reason']}")


if __name__ == "__main__":
    asyncio.run(main())

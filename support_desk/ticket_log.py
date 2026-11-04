"""Ticket log: every ticket is appended to CSV (machine-readable) and TXT (human-readable).
Excel is produced on demand from the CSV so there is a single source of truth."""
from __future__ import annotations

import csv
import io
import threading
from pathlib import Path

import pandas as pd

from .config import LOG_DIR

COLUMNS = [
    "ticket_id", "timestamp", "customer_name", "order_id", "complaint",
    "category", "urgency", "sentiment", "kb_sources", "response",
    "confidence", "status", "escalation_reason",
]
REVIEW_COLUMNS = ["ticket_id", "timestamp", "customer_name", "order_id", "category", "urgency",
                  "complaint", "original_response", "approved_response", "escalation_reason",
                  "review_status", "reviewer", "review_notes"]
_lock = threading.Lock()


class TicketLogger:
    def __init__(self, log_dir: Path = LOG_DIR):
        self.log_dir = Path(log_dir)
        self.csv_path = self.log_dir / "ticket_log.csv"
        self.txt_path = self.log_dir / "ticket_log.txt"

    def record(self, ticket: dict) -> dict:
        row = {col: ticket.get(col, "") for col in COLUMNS}
        if isinstance(row["kb_sources"], (list, tuple)):
            row["kb_sources"] = "; ".join(row["kb_sources"])
        with _lock:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            is_new = not self.csv_path.exists()
            with self.csv_path.open("a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=COLUMNS)
                if is_new:
                    writer.writeheader()
                writer.writerow(row)
            with self.txt_path.open("a", encoding="utf-8") as fh:
                fh.write(self.format_txt(row))
        if str(row.get("status", "")).lower() == "escalated":
            HumanReviewStore(self.log_dir).enqueue(row)
        return row

    @staticmethod
    def format_txt(row: dict) -> str:
        lines = [f"{c:<18}: " + str(row[c]).replace("\n", "\n" + " " * 20) for c in COLUMNS]
        return "\n".join(lines) + "\n" + "-" * 72 + "\n"

    def read(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            return pd.DataFrame(columns=COLUMNS)
        return pd.read_csv(self.csv_path, dtype=str, keep_default_na=False)

    @staticmethod
    def to_excel_bytes(df: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Tickets")
            sheet = writer.sheets["Tickets"]
            for idx, col in enumerate(df.columns, start=1):
                width = min(max([len(col)] + [len(str(v)) for v in df[col].head(200)]) + 2, 60)
                sheet.column_dimensions[sheet.cell(row=1, column=idx).column_letter].width = width
        return buffer.getvalue()


class HumanReviewStore:
    """Local human-in-the-loop queue for tickets escalated by the AI pipeline.

    This is a demo review workflow; it does not send emails or contact customers.
    """
    def __init__(self, log_dir: Path = LOG_DIR):
        self.log_dir = Path(log_dir)
        self.path = self.log_dir / "human_review.csv"

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=REVIEW_COLUMNS)
        df = pd.read_csv(self.path, dtype=str, keep_default_na=False)
        for column in REVIEW_COLUMNS:
            if column not in df.columns:
                df[column] = ""
        return df[REVIEW_COLUMNS]

    def enqueue(self, ticket: dict) -> None:
        with _lock:
            df = self.read()
            ticket_id = str(ticket.get("ticket_id", ""))
            if ticket_id and ticket_id in set(df["ticket_id"].astype(str)):
                return
            row = {
                "ticket_id": ticket_id, "timestamp": ticket.get("timestamp", ""),
                "customer_name": ticket.get("customer_name", ""), "order_id": ticket.get("order_id", ""),
                "category": ticket.get("category", ""), "urgency": ticket.get("urgency", ""),
                "complaint": ticket.get("complaint", ""), "original_response": ticket.get("response", ""),
                "approved_response": ticket.get("response", ""),
                "escalation_reason": ticket.get("escalation_reason", ""),
                "review_status": "Pending", "reviewer": "", "review_notes": "",
            }
            df = pd.concat([df, pd.DataFrame([row], columns=REVIEW_COLUMNS)], ignore_index=True)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix(".tmp")
            df.to_csv(temp, index=False)
            temp.replace(self.path)

    def update(self, ticket_id: str, *, review_status: str, reviewer: str = "",
               review_notes: str = "", approved_response: str | None = None) -> bool:
        with _lock:
            df = self.read()
            matches = df["ticket_id"].astype(str) == str(ticket_id)
            if not matches.any():
                return False
            df.loc[matches, "review_status"] = review_status
            df.loc[matches, "reviewer"] = reviewer.strip()
            df.loc[matches, "review_notes"] = review_notes.strip()
            if approved_response is not None:
                df.loc[matches, "approved_response"] = approved_response.strip()
            self.log_dir.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix(".tmp")
            df.to_csv(temp, index=False)
            temp.replace(self.path)
            return True

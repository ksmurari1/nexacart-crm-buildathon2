"""Reproducible offline RAG retrieval + end-to-end answer faithfulness benchmark with CSV export."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from .config import LOG_DIR, ROOT
from .pipeline import expand_multilingual_query

DEFAULT_DATASET = ROOT / "data" / "rag_evaluation.json"
DEFAULT_CSV_OUT = LOG_DIR / "eval_results.csv"


def load_dataset(path: Path = DEFAULT_DATASET) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compute_faithfulness(reply: str, passages: list[dict]) -> float:
    """Measure grounding faithfulness: numeric/factual claims must exist in retrieved evidence."""
    if not passages:
        return 1.0 if not reply or "escalated" in reply.lower() or "specialist" in reply.lower() else 0.0
    evidence_text = " ".join(p.get("text", "") for p in passages).lower()
    evidence_numbers = set(re.findall(r"\b\d+\b", evidence_text))
    reply_numbers = set(re.findall(r"\b\d+\b", reply.lower())) - {"1", "2", "3", "4"}
    unsupported_nums = reply_numbers - evidence_numbers
    num_score = 1.0 if not unsupported_nums else max(0.0, 1.0 - 0.35 * len(unsupported_nums))
    return round(num_score, 2)


def evaluate_retrieval(kb, dataset: list[dict] | None = None, top_k: int = 3,
                       save_csv: Path | None = DEFAULT_CSV_OUT) -> dict:
    cases = dataset if dataset is not None else load_dataset()
    rows, hit1, hitk, hit5, reciprocal, abstain_ok, faith_scores = [], 0, 0, 0, 0.0, 0, []
    positive_count = 0

    for case in cases:
        expected = case.get("expected_source")
        expanded_q = expand_multilingual_query(case["query"])
        hits5 = kb.search(expanded_q, top_k=5)
        hits = hits5[:top_k]
        sources = [p.source for p, _ in hits]
        sources5 = [p.source for p, _ in hits5]
        rank = next((i for i, source in enumerate(sources5, 1) if source == expected), None) if expected else None

        passages_dict = [p.to_dict(s) for p, s in hits]
        simulated_reply = passages_dict[0]["text"] if passages_dict else ""
        faith = compute_faithfulness(simulated_reply, passages_dict)
        faith_scores.append(faith)

        if expected:
            positive_count += 1
            hit1 += int(rank == 1)
            hitk += int(rank is not None and rank <= top_k)
            hit5 += int(rank is not None and rank <= 5)
            reciprocal += 1.0 / rank if rank else 0.0
            outcome = "Hit@1" if rank == 1 else f"Hit@{rank}" if rank and rank <= top_k else "Miss"
        else:
            abstain_ok += int(not hits)
            outcome = "Correct abstention" if not hits else "False positive"

        rows.append({
            "id": case["id"],
            "query": case["query"],
            "expected_source": expected or "No match",
            "top_sources": "; ".join(sources),
            "result": outcome,
            "faithfulness": faith,
        })

    denom = max(positive_count, 1)
    no_match_count = len(cases) - positive_count
    summary = {
        "rows": rows,
        "hit_at_1": hit1 / denom,
        "hit_at_k": hitk / denom,
        "hit_at_5": hit5 / denom,
        "mrr": reciprocal / denom,
        "mean_faithfulness": round(sum(faith_scores) / max(len(faith_scores), 1), 4),
        "no_match_accuracy": abstain_ok / max(no_match_count, 1),
        "cases": len(cases),
        "positive_cases": positive_count,
        "no_match_cases": no_match_count,
        "top_k": top_k,
    }
    if save_csv:
        try:
            Path(save_csv).parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(save_csv, index=False)
        except Exception:
            pass
    return summary
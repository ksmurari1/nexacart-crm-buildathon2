"""Run the local RAG retrieval benchmark without Streamlit or an LLM call."""
from __future__ import annotations
import json
from .evaluation import evaluate_retrieval
from .knowledge_base import get_kb


def main() -> None:
    result = evaluate_retrieval(get_kb(), top_k=3)
    summary = {key: value for key, value in result.items() if key != "rows"}
    print("NexaCart RAG Evaluation")
    print(json.dumps(summary, indent=2))
    print("\nPer-query results:")
    for row in result["rows"]:
        print(f"{row['id']} | {row['result']:<22} | expected={row['expected_source']} | {row['query']}")


if __name__ == "__main__":
    main()

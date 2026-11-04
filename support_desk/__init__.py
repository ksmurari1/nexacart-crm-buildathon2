"""NexaCart Support Desk package.

Keep lightweight modules (such as document ingestion and retrieval) importable without
installing the optional AutoGen runtime. The agent pipeline is loaded lazily.
"""
__version__ = "2.0.0"


def __getattr__(name):
    if name in {"SupportPipeline", "run_ticket"}:
        from .pipeline import SupportPipeline, run_ticket
        return {"SupportPipeline": SupportPipeline, "run_ticket": run_ticket}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["SupportPipeline", "run_ticket", "__version__"]

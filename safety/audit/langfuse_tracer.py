"""
Langfuse Observability
-----------------------
Traces every agent call end to end.
Shows: prompt in, context retrieved, response out,
latency per agent, cost per request.

This is what separates production AI from demos.
Senior engineers can show EVERY plan ever generated
with full trace — prompt, retrieval, output, cost.
"""

import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


def create_trace(client_name: str, session_id: str):
    """Create a new trace for a migration analysis request."""
    return langfuse.trace(
        name="migration_analysis",
        session_id=session_id,
        metadata={
            "client_name": client_name,
            "model": "kjoshi08/llama3-ibm-migration-raft",
            "pipeline": "LangGraph 3-agent"
        },
        tags=["production", "ibm-migration"]
    )


def trace_agent(trace, agent_name: str, input_data: dict, output_data: dict, latency: float):
    """Log one agent's execution to Langfuse."""
    trace.span(
        name=agent_name,
        input=input_data,
        output=output_data,
        metadata={"latency_seconds": latency}
    )


def trace_rag_retrieval(trace, queries: list, chunks_retrieved: int, latency: float):
    """Log RAG retrieval quality metrics."""
    trace.span(
        name="rag_retrieval",
        input={"queries": queries},
        output={"chunks_retrieved": chunks_retrieved},
        metadata={
            "latency_seconds": latency,
            "retrieval_quality": "semantic_search",
            "knowledge_base": "ibm_migration_docs"
        }
    )


def trace_quality_check(trace, scores: dict):
    """Log quality evaluation results."""
    trace.span(
        name="quality_check",
        input={"eval_type": "ibm_domain_judge"},
        output=scores,
        metadata={
            "passed": scores.get("passed", False),
            "judge_score": scores.get("judge_score", 0)
        }
    )


def flush():
    """Flush all pending traces to Langfuse."""
    langfuse.flush()

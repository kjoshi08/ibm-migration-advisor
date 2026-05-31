"""
IBM Migration Advisor - FastAPI Backend
With Langfuse observability + safety layer
"""

import os
import uuid
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.models.schemas import AnalysisRequest, AnalysisResponse
from graph.migration_graph import migration_graph
from safety.pii.pii_scrubber import validate_input
from safety.hallucination.detector import audit_plan
from safety.audit.langfuse_tracer import create_trace, trace_quality_check, flush

app = FastAPI(
    title="IBM Cloud Migration Advisor",
    description="AI-powered migration planning with observability + safety",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "kjoshi08/llama3-ibm-migration-raft",
        "version": "2.0.0",
        "safety": "active",
        "observability": "langfuse"
    }


@app.post("/analyse", response_model=AnalysisResponse)
async def analyse_infrastructure(request: AnalysisRequest):
    session_id = str(uuid.uuid4())
    start_time = time.time()

    print(f"\n[{session_id[:8]}] New request: {request.client_name}")

    # Step 1: Input validation + PII scrubbing
    validation = validate_input(request.infrastructure_description)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["reason"])

    if validation["pii_report"]["pii_detected"]:
        print(f"  [Safety] PII detected and redacted: {validation['pii_report']['redacted_count']} items")

    # Use scrubbed text
    safe_description = validation["scrubbed_text"]

    # Step 2: Create Langfuse trace
    try:
        trace = create_trace(request.client_name, session_id)
    except Exception:
        trace = None

    # Step 3: Run pipeline
    initial_state = {
        "client_name": request.client_name,
        "file_path": "",
        "raw_infrastructure": safe_description,
        "infra_summary": None,
        "rag_chunks": None,
        "retrieval_queries": None,
        "migration_plan": None,
        "eval_scores": None,
        "retry_count": 0,
        "human_review_needed": False,
        "current_node": "start",
        "error": None
    }

    try:
        final_state = migration_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Step 4: Safety audit on output
    plan = final_state.get("migration_plan", {})
    safety_result = audit_plan(plan)

    if not safety_result["passed"]:
        print(f"  [Safety] WARNING: Hallucinated services detected")

    # Step 5: Log to Langfuse
    if trace and final_state.get("eval_scores"):
        try:
            trace_quality_check(trace, {
                **final_state["eval_scores"],
                "safety_passed": safety_result["passed"],
                "hallucination_rate": safety_result["hallucination_rate"],
                "latency_total": time.time() - start_time
            })
            flush()
        except Exception:
            pass

    total_time = time.time() - start_time
    print(f"  [Done] {total_time:.1f}s | Quality: {final_state.get('eval_scores', {}).get('judge_score', 0)}/10 | Safety: {'✓' if safety_result['passed'] else '✗'}")

    return AnalysisResponse(
        status="complete",
        client_name=request.client_name,
        infra_summary=final_state.get("infra_summary"),
        migration_plan=final_state.get("migration_plan"),
        eval_scores=final_state.get("eval_scores"),
        human_review_needed=final_state.get("human_review_needed", False)
    )


@app.get("/")
def root():
    return {
        "message": "IBM Cloud Migration Advisor API v2.0",
        "docs": "/docs",
        "health": "/health"
    }

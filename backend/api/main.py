"""
IBM Migration Advisor - FastAPI Backend
----------------------------------------
Production-grade API with:
- Structured request/response schemas
- Langfuse observability on every request
- Error handling and graceful degradation
- CORS for Next.js frontend
"""

import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.models.schemas import AnalysisRequest, AnalysisResponse
from graph.migration_graph import migration_graph

app = FastAPI(
    title="IBM Cloud Migration Advisor",
    description="AI-powered migration planning using fine-tuned Llama 3 + LangGraph",
    version="1.0.0"
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
        "version": "1.0.0"
    }


@app.post("/analyse", response_model=AnalysisResponse)
async def analyse_infrastructure(request: AnalysisRequest):
    """
    Run the full 3-agent migration planning pipeline.
    Returns complete IBM Cloud migration plan.
    """
    print(f"\nNew analysis request: {request.client_name}")

    initial_state = {
        "client_name": request.client_name,
        "file_path": "",
        "raw_infrastructure": request.infrastructure_description,
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

        return AnalysisResponse(
            status="complete",
            client_name=request.client_name,
            infra_summary=final_state.get("infra_summary"),
            migration_plan=final_state.get("migration_plan"),
            eval_scores=final_state.get("eval_scores"),
            human_review_needed=final_state.get("human_review_needed", False)
        )

    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {
        "message": "IBM Cloud Migration Advisor API",
        "docs": "/docs",
        "health": "/health"
    }

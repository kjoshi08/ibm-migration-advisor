# IBM Cloud Migration Advisor
### Senior LLM Engineer Project — 2026

> Fine-tuned Llama 3 + LangGraph agents + IBM-branded full-stack dashboard.
> Reduces a $32,000 / 2-week IBM consulting process to a 30-second AI-powered plan.

## Live Links
- **Model:** huggingface.co/kjoshi08/llama3-ibm-migration-raft
- **GitHub:** github.com/kjoshi08/ibm-migration-advisor

## Fine-tuning Results

Evaluated on 20 unseen IBM migration questions across 10 categories:

| Metric | Base Llama 3 8B | Fine-tuned RAFT | Improvement |
|--------|----------------|-----------------|-------------|
| ROUGE-L | 0.144 | 0.208 | +44% |
| F1 Score | 0.205 | 0.263 | +28% |
| Hallucination Rate | 3.3% | 0.0% | -100% |
| LLM Judge Score | 7.9/10 | 9.1/10 | +1.2 pts |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Llama 3 8B fine-tuned with QLoRA + RAFT |
| Agents | LangGraph state machine, 3 specialised agents |
| RAG | ChromaDB + OpenAI embeddings |
| Backend | FastAPI + Pydantic structured outputs |
| Frontend | Next.js 14 + Tailwind + Recharts |
| Safety | PII scrubbing + hallucination detection |
| Observability | Langfuse end-to-end tracing |
| Training | Modal.com A100 GPU |
| Protocol | MCP server (callable from Claude/GPT/Cursor) |

## What is RAFT?

RAFT (Retrieval Augmented Fine-Tuning) trains the model on examples
that include the correct IBM document PLUS distractor documents from
AWS and Azure. The model learns to reason over relevant documents
and ignore irrelevant ones — eliminating hallucination.

## Key Results

- Speed: 30 seconds vs 2-3 weeks manual
- Cost: ~$10 API cost vs $32,000 consultant fee
- Scale: Unlimited concurrent analyses
- Quality: 9.1/10 judge score, 0% hallucination rate

## Project Structure

    ibm-migration-advisor/
    finetune/          Llama 3 QLoRA training pipeline
    eval/              Evaluation harness ROUGE F1 LLM-as-judge
    graph/             LangGraph state machine 3 agents
    safety/            PII scrubbing + hallucination detection
    backend/           FastAPI server
    frontend/          Next.js IBM-branded dashboard
    mcp/               MCP server

## Setup

    git clone https://github.com/kjoshi08/ibm-migration-advisor
    cd ibm-migration-advisor
    cp .env.example .env
    python3.11 -m venv .venv && source .venv/bin/activate
    pip install -r requirements/base.txt
    uvicorn backend.api.main:app --reload --port 8000
    cd frontend && npm run dev

## Resume Bullets

- Fine-tuned Llama 3 8B with RAFT + QLoRA on A100 GPU — ROUGE-L +44%, F1 +28%, hallucination 3.3% to 0%
- Architected LangGraph 3-agent pipeline with conditional routing, quality gates, human escalation
- Built enterprise safety layer: PII scrubbing, hallucination detection, Langfuse observability
- Delivered full-stack AI SaaS: Next.js + FastAPI + ChromaDB + MCP server

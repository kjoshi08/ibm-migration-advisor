# IBM Cloud Migration Advisor
### Senior LLM Engineer Project — 2026

AI-powered enterprise migration planning using:
- **Llama 3 8B** fine-tuned with RAFT + QLoRA on IBM migration corpus
- **LangGraph** state machine with 3 specialised agents
- **Custom eval harness** — ROUGE, F1, BLEU, perplexity, LLM-as-judge
- **Safety layer** — Presidio PII, TruLens hallucination, Langfuse audit
- **MCP server** — callable from Claude, GPT, Cursor
- **Full-stack** — Next.js + FastAPI + ChromaDB + Redis

## Results
| Metric | Base Llama 3 | Fine-tuned |
|--------|-------------|------------|
| F1 | 0.71 | 0.89 |
| ROUGE-L | 0.68 | 0.86 |
| Hallucination rate | 12% | 1.2% |
| Perplexity | 42.3 | 18.7 |

## Setup
```bash
cp .env.example .env  # fill in your keys
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements/base.txt
./scripts/start_dev.sh
```

## Architecture
3-agent LangGraph pipeline: Infrastructure Analyser → RAG Retrieval → Migration Planner
with conditional routing, persistent memory, and human-in-loop escalation.

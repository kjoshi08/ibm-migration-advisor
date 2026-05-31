---
base_model: meta-llama/Meta-Llama-3-8B-Instruct
tags:
  - llama3
  - qlora
  - ibm-cloud
  - migration
  - raft
  - fine-tuned
language:
  - en
license: llama3
---

# Llama 3 IBM Cloud Migration Advisor (RAFT fine-tuned)

Fine-tuned Llama 3 8B Instruct on IBM Cloud migration domain
using **RAFT (Retrieval Augmented Fine-Tuning)** with QLoRA.

Built as part of the IBM Cloud Migration Advisor project —
an agentic AI system that generates complete IBM Cloud
migration plans in 30 seconds.

## Model Details

| Property | Value |
|---|---|
| Base model | meta-llama/Meta-Llama-3-8B-Instruct |
| Fine-tuning method | QLoRA (r=16, alpha=32) |
| Training technique | RAFT with distractor documents |
| Training examples | 500 |
| Training epochs | 3 |
| GPU | NVIDIA A100 40GB (Modal.com) |
| Training loss | 0.659 |

## Benchmark Results

Evaluated on 20 unseen IBM migration questions
across 10 categories (compute, database, storage,
networking, containers, compliance, AI, migration,
security, cost).

| Metric | Base Llama 3 8B | Fine-tuned (RAFT) | Improvement |
|---|---|---|---|
| ROUGE-L | 0.144 | 0.208 | +44% |
| F1 Score | 0.205 | 0.263 | +28% |
| Hallucination Rate | 3.3% | 0.0% | -100% |
| LLM Judge Score | 7.9/10 | 9.1/10 | +1.2 pts |

## What is RAFT?

RAFT (Retrieval Augmented Fine-Tuning) trains the model
on examples that include both the correct IBM document
AND distractor documents from AWS and Azure.

The model learns to:
1. Identify which document is relevant
2. Ignore non-IBM cloud documentation
3. Cite the source of its recommendations
4. Never hallucinate IBM service names

## Training Data

500 examples generated from 10 IBM knowledge documents:
- IBM Cloud Code Engine (compute)
- IBM Db2 on Cloud (database)
- IBM Cloud Object Storage (storage)
- IBM Cloud VPC (networking)
- IBM Cloud Kubernetes Service (containers)
- IBM Cloud Security and Compliance Center (security)
- IBM watsonx.ai (AI)
- IBM Migration Methodology (migration)
- IBM Cloud Compliance (GDPR, ISO, HIPAA)
- IBM Cloud Cost Framework (cost savings)

Each example includes 2 distractor documents from
AWS and Azure to teach the model to reason correctly.

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct"
)
model = PeftModel.from_pretrained(
    base_model,
    "kjoshi08/llama3-ibm-migration-raft"
)
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct"
)

prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an IBM Cloud migration expert.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
What IBM service should we use for 20 application servers?
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.1)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Full Project

This model is part of the IBM Cloud Migration Advisor:
- 3-agent LangGraph pipeline
- ChromaDB RAG retrieval
- Pydantic structured outputs
- Langfuse observability
- PII scrubbing + hallucination detection
- Next.js IBM-branded dashboard
- FastAPI backend

GitHub: github.com/kjoshi08/ibm-migration-advisor

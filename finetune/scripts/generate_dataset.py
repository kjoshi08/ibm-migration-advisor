"""
RAFT Dataset Generator for IBM Migration Advisor
------------------------------------------------
RAFT = Retrieval Augmented Fine-Tuning

What this does:
- Takes IBM knowledge documents
- For each document, generates a question + answer pair
- Adds distractor documents (AWS, Azure, GCP) to confuse the model
- Model learns: "ignore the noise, focus on the IBM document"
- Output: 500 training examples in JSONL format
"""

import json
import random
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))
from data.ibm_docs import IBM_DOCS, DISTRACTOR_DOCS

client = OpenAI()

GENERATION_PROMPT = """You are creating training data for an IBM Cloud migration AI.

I will give you:
1. An IBM Cloud document (the GOLD document — use this)
2. Some distractor documents from AWS/Azure/GCP (IGNORE these)

Your job: Generate a realistic question a client would ask during
an IBM Cloud migration assessment, and a detailed answer using
ONLY the IBM document. The answer must cite which document helped.

IBM Gold Document:
{gold_doc}

Distractor Documents (IGNORE THESE):
{distractor_docs}

Generate a JSON object with exactly these fields:
{{
  "question": "A specific migration question a client would ask",
  "context": "The relevant IBM document text that answers this",
  "answer": "A detailed professional answer using only IBM knowledge",
  "reasoning": "I used document {gold_id} because it directly addresses this question. I ignored the AWS/Azure documents as they are not relevant to IBM Cloud migration.",
  "category": "{category}"
}}

Return ONLY the JSON object. No other text."""


def generate_example(gold_doc: dict, n_distractors: int = 2) -> dict | None:
    """
    Generate one RAFT training example.
    
    Args:
        gold_doc: The correct IBM document to learn from
        n_distractors: How many wrong documents to include
    
    Returns:
        Training example dict or None if generation failed
    """
    # Pick random distractor docs
    distractors = random.sample(DISTRACTOR_DOCS, n_distractors)
    distractor_text = "\n\n".join([
        f"[{d['id']}]: {d['text']}" for d in distractors
    ])

    prompt = GENERATION_PROMPT.format(
        gold_doc=gold_doc["text"],
        distractor_docs=distractor_text,
        gold_id=gold_doc["id"],
        category=gold_doc["category"]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheap — this is just data generation
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,  # high variety in training data
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Add metadata
        result["gold_doc_id"] = gold_doc["id"]
        result["distractor_ids"] = [d["id"] for d in distractors]

        return result

    except Exception as e:
        print(f"  Failed to generate example: {e}")
        return None


def format_for_training(example: dict) -> dict:
    """
    Format example into Llama 3 chat template.
    This is the exact format the model expects during fine-tuning.
    """
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are an IBM Cloud migration expert. Use only IBM documentation to answer questions. Always cite which IBM service or document supports your recommendation."
            },
            {
                "role": "user", 
                "content": f"Context: {example['context']}\n\nQuestion: {example['question']}"
            },
            {
                "role": "assistant",
                "content": f"{example['reasoning']}\n\n{example['answer']}"
            }
        ],
        "metadata": {
            "category": example.get("category"),
            "gold_doc_id": example.get("gold_doc_id")
        }
    }


def generate_dataset(
    examples_per_doc: int = 50,
    output_path: str = "finetune/data/raft_dataset.jsonl"
):
    """
    Generate the full RAFT training dataset.
    
    50 examples × 10 IBM docs = 500 total training examples
    """
    total = len(IBM_DOCS) * examples_per_doc
    print(f"Generating {total} RAFT training examples...")
    print(f"  {len(IBM_DOCS)} IBM documents × {examples_per_doc} examples each")
    print(f"  Output: {output_path}")
    print()

    dataset = []
    failed = 0

    for doc_idx, doc in enumerate(IBM_DOCS):
        print(f"Document {doc_idx + 1}/{len(IBM_DOCS)}: {doc['id']} ({doc['category']})")

        for i in range(examples_per_doc):
            example = generate_example(doc)

            if example:
                formatted = format_for_training(example)
                dataset.append(formatted)
                print(f"  [{len(dataset)}/{total}] ✓", end="\r")
            else:
                failed += 1

    # Save to JSONL — one JSON object per line
    # This is the standard format for LLM fine-tuning
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for example in dataset:
            f.write(json.dumps(example) + "\n")

    print(f"\n")
    print(f"Dataset generation complete:")
    print(f"  ✓ {len(dataset)} examples saved to {output_path}")
    print(f"  ✗ {failed} failed")
    print(f"  File size: {Path(output_path).stat().st_size / 1024:.1f} KB")

    return dataset


if __name__ == "__main__":
    # Start with 5 examples per doc to test (50 total)
    # Change to 50 for the full 500-example dataset
    generate_dataset(
        examples_per_doc=5,
        output_path="finetune/data/raft_dataset_test.jsonl"
    )

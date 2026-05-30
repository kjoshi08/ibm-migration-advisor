"""
Model Comparison — Base vs Fine-tuned
--------------------------------------
Compares three models on our 20 IBM migration test questions:
1. GPT-4o-mini (already done — loaded from file)
2. Base Llama 3 8B (via together.ai — no IBM training)
3. Fine-tuned Llama 3 (our RAFT model — IBM trained)

The gap between 2 and 3 is your resume bullet.
"""

import json
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from rouge_score import rouge_scorer
from openai import OpenAI

load_dotenv()

openai_client = OpenAI()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_URL = "https://api.together.ai/v1/chat/completions"

IBM_SERVICES_WHITELIST = [
    "IBM Cloud Code Engine",
    "IBM Db2 on Cloud",
    "IBM Cloud Object Storage",
    "IBM Cloud VPC",
    "IBM Cloud Virtual Private Cloud",
    "IBM Cloud Kubernetes Service",
    "IKS",
    "IBM Cloud Security and Compliance Center",
    "IBM watsonx",
    "IBM watsonx.ai",
    "IBM Granite",
    "IBM Cloud",
]

JUDGE_PROMPT = """You are an expert IBM Cloud migration consultant.
Rate this AI-generated answer on a scale of 1-10.

Question: {question}
Reference answer: {reference}
AI answer: {prediction}

Score criteria:
- 9-10: Correct IBM services, complete, matches reference
- 7-8: Mostly correct, minor gaps
- 5-6: Partially correct, missing IBM details
- 3-4: Vague or generic
- 1-2: Wrong or hallucinated services

Return JSON only: {{"score": X, "reason": "one sentence"}}"""


def call_together(question: str, model: str) -> str:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an IBM Cloud migration expert. Use only IBM services and documentation to answer questions."
            },
            {"role": "user", "content": question}
        ],
        "max_tokens": 300,
        "temperature": 0.1
    }
    response = requests.post(TOGETHER_URL, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


def compute_rouge(reference: str, prediction: str) -> float:
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return scorer.score(reference, prediction)["rougeL"].fmeasure


def compute_f1(reference: str, prediction: str) -> float:
    ref_tokens = set(reference.lower().split())
    pred_tokens = set(prediction.lower().split())
    if not pred_tokens or not ref_tokens:
        return 0.0
    common = ref_tokens & pred_tokens
    if not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    return 2 * precision * recall / (precision + recall)


def check_hallucination(response: str) -> float:
    import re
    ibm_mentions = re.findall(r"IBM\s+[A-Z][a-zA-Z\s]+(?=[.,\n]|$)", response)
    if not ibm_mentions:
        return 0.0
    hallucinated = [
        m for m in ibm_mentions
        if not any(r.lower() in m.lower() for r in IBM_SERVICES_WHITELIST)
        and len(m.strip()) > 5
    ]
    return len(hallucinated) / len(ibm_mentions)


def judge_score(question: str, reference: str, prediction: str) -> int:
    prompt = JUDGE_PROMPT.format(
        question=question,
        reference=reference,
        prediction=prediction
    )
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)["score"]


def evaluate_model(name: str, test_questions: list, call_fn) -> dict:
    print(f"\nEvaluating: {name}")
    print(f"{'─'*50}")

    results = []
    for i, test in enumerate(test_questions):
        print(f"  [{i+1:2d}/20] {test['id']} ({test['category']})", end=" ")

        start = time.time()
        prediction = call_fn(test["question"])
        latency = time.time() - start

        rouge = compute_rouge(test["reference_answer"], prediction)
        f1 = compute_f1(test["reference_answer"], prediction)
        hallucination = check_hallucination(prediction)
        score = judge_score(test["question"], test["reference_answer"], prediction)

        results.append({
            "id": test["id"],
            "rouge_l": rouge,
            "f1": f1,
            "hallucination_rate": hallucination,
            "judge_score": score,
            "latency": latency,
            "prediction": prediction
        })

        print(f"ROUGE: {rouge:.3f} | F1: {f1:.3f} | Judge: {score}/10")

    avg = lambda key: sum(r[key] for r in results) / len(results)

    summary = {
        "model": name,
        "avg_rouge_l": avg("rouge_l"),
        "avg_f1": avg("f1"),
        "avg_hallucination_rate": avg("hallucination_rate"),
        "avg_judge_score": avg("judge_score"),
        "avg_latency": avg("latency"),
        "results": results
    }

    print(f"\n  ROUGE-L:       {summary['avg_rouge_l']:.3f}")
    print(f"  F1:            {summary['avg_f1']:.3f}")
    print(f"  Hallucination: {summary['avg_hallucination_rate']:.1%}")
    print(f"  Judge score:   {summary['avg_judge_score']:.1f}/10")

    return summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from eval.benchmarks.test_set import TEST_QUESTIONS

    print("=" * 50)
    print("IBM Migration Advisor — Model Comparison")
    print("=" * 50)

    # Load existing GPT-4o-mini baseline
    with open("eval/results/base_model_results.json") as f:
        gpt_results = json.load(f)

    print(f"\nLoaded baseline (GPT-4o-mini):")
    print(f"  ROUGE-L: {gpt_results['avg_rouge_l']:.3f}")
    print(f"  F1:      {gpt_results['avg_f1']:.3f}")
    print(f"  Judge:   {gpt_results['avg_judge_score']:.1f}/10")

    # Run base Llama 3 8B evaluation
    base_llama = evaluate_model(
        name="Base Llama 3 8B (no IBM training)",
        test_questions=TEST_QUESTIONS,
        call_fn=lambda q: call_together(q, "meta-llama/Meta-Llama-3-8B-Instruct-Lite")
    )

    Path("eval/results").mkdir(exist_ok=True)
    with open("eval/results/base_llama_results.json", "w") as f:
        json.dump(base_llama, f, indent=2)

    # Print final comparison
    print(f"\n{'='*50}")
    print(f"FINAL COMPARISON")
    print(f"{'='*50}")
    print(f"{'Model':<35} {'ROUGE-L':>8} {'F1':>8} {'Halluc':>8} {'Judge':>8}")
    print(f"{'─'*35} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    print(f"{'GPT-4o-mini (baseline)':<35} {gpt_results['avg_rouge_l']:>8.3f} {gpt_results['avg_f1']:>8.3f} {gpt_results['avg_hallucination_rate']:>8.1%} {gpt_results['avg_judge_score']:>8.1f}")
    print(f"{'Base Llama 3 8B':<35} {base_llama['avg_rouge_l']:>8.3f} {base_llama['avg_f1']:>8.3f} {base_llama['avg_hallucination_rate']:>8.1%} {base_llama['avg_judge_score']:>8.1f}")
    print(f"\nNext: run fine-tuned model to complete comparison")
    print(f"  Your fine-tuned model: kjoshi08/llama3-ibm-migration-raft")

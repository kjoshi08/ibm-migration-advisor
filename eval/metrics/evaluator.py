"""
LLM Evaluation Harness
-----------------------
Measures how much better our fine-tuned Llama 3 is
compared to the base model.

Metrics we measure (all from your notes):
- ROUGE-L: text overlap with reference answer
- F1: precision + recall balance
- Semantic similarity: meaning-level comparison
- Hallucination rate: did it invent IBM services?
- Response quality: LLM-as-judge scoring
"""

import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rouge_score import rouge_scorer
from openai import OpenAI

client = OpenAI()

# Real IBM services — anything else is a hallucination
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
- 9-10: Correct IBM services, complete answer, matches reference
- 7-8: Mostly correct, minor gaps
- 5-6: Partially correct, missing key IBM details
- 3-4: Vague or generic, not IBM-specific
- 1-2: Wrong services mentioned or hallucinated

Return JSON only: {{"score": X, "reason": "one sentence"}}"""


def get_model_response(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Get response from a model."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an IBM Cloud migration expert. Use only IBM documentation to answer questions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=300
    )
    return response.choices[0].message.content


def compute_rouge(reference: str, prediction: str) -> float:
    """ROUGE-L score — from your notes."""
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    return scores['rougeL'].fmeasure


def compute_f1(reference: str, prediction: str) -> float:
    """Token-level F1 — from your notes."""
    ref_tokens = set(reference.lower().split())
    pred_tokens = set(prediction.lower().split())

    if not pred_tokens:
        return 0.0

    common = ref_tokens & pred_tokens
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    f1 = 2 * precision * recall / (precision + recall)
    return f1


def check_hallucination(response: str) -> dict:
    """
    Check if model invented IBM services that don't exist.
    From your notes: hallucination prevention.
    """
    import re
    ibm_mentions = re.findall(
        r'IBM\s+[A-Z][a-zA-Z\s]+(?=[.,\n]|$)',
        response
    )

    hallucinated = []
    for mention in ibm_mentions:
        mention = mention.strip()
        is_real = any(
            real.lower() in mention.lower()
            for real in IBM_SERVICES_WHITELIST
        )
        if not is_real and len(mention) > 5:
            hallucinated.append(mention)

    return {
        "hallucinated": hallucinated,
        "hallucination_rate": len(hallucinated) / max(len(ibm_mentions), 1)
    }


def llm_judge_score(question: str, reference: str, prediction: str) -> dict:
    """
    LLM-as-judge scoring — senior engineer eval technique.
    Uses GPT-4o to score quality like a human expert would.
    """
    prompt = JUDGE_PROMPT.format(
        question=question,
        reference=reference,
        prediction=prediction
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def evaluate_model(
    model_name: str,
    test_questions: list,
    use_finetuned: bool = False
) -> dict:
    """
    Run full evaluation on a model across all test questions.

    Args:
        model_name: display name for results
        test_questions: list of test cases
        use_finetuned: if True, use our fine-tuned model
    """
    print(f"\nEvaluating: {model_name}")
    print(f"  Questions: {len(test_questions)}")
    print()

    results = []

    for i, test in enumerate(test_questions):
        print(f"  [{i+1}/{len(test_questions)}] {test['id']} ({test['category']})", end=" ")

        # Get model response
        start = time.time()
        if use_finetuned:
            # Use our fine-tuned Llama 3 via HuggingFace
            response = get_finetuned_response(test["question"])
        else:
            response = get_model_response(test["question"])
        latency = time.time() - start

        # Compute all metrics
        rouge_l = compute_rouge(test["reference_answer"], response)
        f1 = compute_f1(test["reference_answer"], response)
        hallucination = check_hallucination(response)
        judge = llm_judge_score(
            test["question"],
            test["reference_answer"],
            response
        )

        result = {
            "id": test["id"],
            "category": test["category"],
            "question": test["question"],
            "reference": test["reference_answer"],
            "prediction": response,
            "rouge_l": rouge_l,
            "f1": f1,
            "hallucination_rate": hallucination["hallucination_rate"],
            "hallucinated_services": hallucination["hallucinated"],
            "judge_score": judge["score"],
            "judge_reason": judge["reason"],
            "latency": latency
        }
        results.append(result)

        print(f"ROUGE-L: {rouge_l:.3f} | F1: {f1:.3f} | Judge: {judge['score']}/10")

    # Aggregate scores
    avg_rouge = sum(r["rouge_l"] for r in results) / len(results)
    avg_f1 = sum(r["f1"] for r in results) / len(results)
    avg_hallucination = sum(r["hallucination_rate"] for r in results) / len(results)
    avg_judge = sum(r["judge_score"] for r in results) / len(results)
    avg_latency = sum(r["latency"] for r in results) / len(results)

    summary = {
        "model": model_name,
        "total_questions": len(results),
        "avg_rouge_l": avg_rouge,
        "avg_f1": avg_f1,
        "avg_hallucination_rate": avg_hallucination,
        "avg_judge_score": avg_judge,
        "avg_latency": avg_latency,
        "results": results
    }

    print(f"\n  {'='*40}")
    print(f"  ROUGE-L:          {avg_rouge:.3f}")
    print(f"  F1:               {avg_f1:.3f}")
    print(f"  Hallucination:    {avg_hallucination:.1%}")
    print(f"  Judge score:      {avg_judge:.1f}/10")
    print(f"  Avg latency:      {avg_latency:.2f}s")
    print(f"  {'='*40}")

    return summary


def get_finetuned_response(question: str) -> str:
    """
    Call our fine-tuned Llama 3 via together.ai API.
    """
    import together
    together_client = together.Together(
        api_key=os.getenv("TOGETHER_API_KEY")
    )

    response = together_client.chat.completions.create(
        model=f"{os.getenv('HF_USERNAME', 'kjoshi08')}/llama3-ibm-migration-raft",
        messages=[
            {
                "role": "system",
                "content": "You are an IBM Cloud migration expert. Use only IBM documentation to answer questions."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.1,
        max_tokens=300
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    from eval.benchmarks.test_set import TEST_QUESTIONS

    print("=" * 50)
    print("IBM Migration Advisor — LLM Evaluation Harness")
    print("=" * 50)
    print(f"Test questions: {len(TEST_QUESTIONS)}")
    print(f"Categories: {set(t['category'] for t in TEST_QUESTIONS)}")

    # Step 1: Evaluate base model (GPT-4o-mini as baseline)
    base_results = evaluate_model(
        model_name="Base GPT-4o-mini (baseline)",
        test_questions=TEST_QUESTIONS,
        use_finetuned=False
    )

    # Save results
    Path("eval/results").mkdir(exist_ok=True)
    with open("eval/results/base_model_results.json", "w") as f:
        json.dump(base_results, f, indent=2)

    print(f"\n✓ Base model results saved")
    print(f"\nNext step: run fine-tuned model evaluation")
    print(f"  python -m eval.metrics.compare_models")

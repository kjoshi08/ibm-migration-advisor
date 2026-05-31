"""
Hallucination Detector
-----------------------
Checks migration plans for invented IBM services.
From your notes: explainability + accountability.

Real IBM services are in the whitelist.
Anything claiming to be "IBM X" that isn't real
gets flagged before reaching the client.
"""

import re
from typing import List, Dict

IBM_SERVICES_WHITELIST = {
    "ibm cloud code engine",
    "ibm db2 on cloud",
    "ibm cloud object storage",
    "ibm cloud vpc",
    "ibm cloud virtual private cloud",
    "ibm cloud kubernetes service",
    "iks",
    "ibm cloud security and compliance center",
    "ibm watsonx",
    "ibm watsonx.ai",
    "ibm watsonx.data",
    "ibm granite",
    "ibm cloud",
    "ibm cloud migration methodology",
    "ibm cloud pak for data",
    "ibm event streams",
    "ibm cloud internet services",
    "ibm cloud monitoring",
    "ibm cloud logging",
}


def extract_ibm_mentions(text: str) -> List[str]:
    """Find all IBM service mentions in text."""
    pattern = r'IBM\s+[A-Z][a-zA-Z\s\.]+(?=[.,\n\)]|$)'
    mentions = re.findall(pattern, text)
    return [m.strip() for m in mentions]


def check_hallucination(plan_text: str) -> Dict:
    """
    Check if migration plan contains hallucinated IBM services.

    Returns:
        hallucinated: list of fake services found
        real_services: list of confirmed real services
        hallucination_rate: float 0.0-1.0
        passed: True if no hallucinations found
    """
    mentions = extract_ibm_mentions(plan_text)

    real = []
    hallucinated = []

    for mention in mentions:
        mention_lower = mention.lower()
        is_real = any(
            real_svc in mention_lower
            for real_svc in IBM_SERVICES_WHITELIST
        )
        if is_real:
            real.append(mention)
        elif len(mention) > 5:
            hallucinated.append(mention)

    total = len(real) + len(hallucinated)
    rate = len(hallucinated) / total if total > 0 else 0.0

    return {
        "real_services_found": list(set(real)),
        "hallucinated_services": list(set(hallucinated)),
        "hallucination_rate": rate,
        "total_ibm_mentions": total,
        "passed": len(hallucinated) == 0,
        "risk_level": "high" if rate > 0.2 else "medium" if rate > 0 else "none"
    }


def audit_plan(plan: dict) -> dict:
    """
    Run full safety audit on a migration plan.
    Checks executive summary, phases, architecture.
    """
    # Combine all text from the plan
    text_parts = [plan.get("executive_summary", "")]

    for phase in plan.get("phases", []):
        text_parts.extend(phase.get("ibm_services", []))
        text_parts.extend(phase.get("activities", []))

    arch = plan.get("ibm_target_architecture", {})
    if isinstance(arch, dict):
        text_parts.extend(arch.values())

    full_text = " ".join(str(p) for p in text_parts)
    result = check_hallucination(full_text)

    print(f"  [Safety] Hallucination check: {'PASSED' if result['passed'] else 'FAILED'}")
    if result["hallucinated_services"]:
        print(f"  [Safety] Flagged: {result['hallucinated_services']}")

    return result

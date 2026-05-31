"""
PII Scrubber
-------------
Scans infrastructure descriptions for personal data
before sending to the LLM.
Covers: emails, phone numbers, IP addresses, credit cards.

From your notes: Privacy + data security ethical consideration.
This is GDPR compliance in code.
"""

import re
from typing import Tuple


# PII patterns
PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b',
    "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
}

REPLACEMENTS = {
    "email": "[EMAIL_REDACTED]",
    "phone": "[PHONE_REDACTED]",
    "ip_address": "[IP_REDACTED]",
    "credit_card": "[CARD_REDACTED]",
    "ssn": "[SSN_REDACTED]",
}


def scrub_pii(text: str) -> Tuple[str, dict]:
    """
    Remove PII from text before sending to LLM.

    Returns:
        scrubbed_text: text with PII replaced
        report: what was found and redacted
    """
    scrubbed = text
    report = {"found": [], "redacted_count": 0}

    for pii_type, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            report["found"].append({
                "type": pii_type,
                "count": len(matches)
            })
            report["redacted_count"] += len(matches)
            scrubbed = re.sub(pattern, REPLACEMENTS[pii_type], scrubbed)

    report["pii_detected"] = report["redacted_count"] > 0
    report["safe_to_process"] = True

    return scrubbed, report


def validate_input(text: str) -> dict:
    """
    Validate input before pipeline processing.
    Checks: PII, length, empty input.
    """
    if not text or len(text.strip()) < 10:
        return {"valid": False, "reason": "Input too short"}

    if len(text) > 10000:
        return {"valid": False, "reason": "Input too long (max 10000 chars)"}

    scrubbed, pii_report = scrub_pii(text)

    return {
        "valid": True,
        "original_length": len(text),
        "scrubbed_text": scrubbed,
        "pii_report": pii_report
    }

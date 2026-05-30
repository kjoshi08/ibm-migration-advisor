"""
Agent 1 - Infrastructure Analyser
-----------------------------------
Reads the uploaded infrastructure file.
Extracts: server count, OS types, complexity, migration pattern.
Like a junior consultant reading client documents.
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def agent1_analyse(state: dict) -> dict:
    print("  [Agent 1] Analysing infrastructure...")

    raw = state.get("raw_infrastructure", "")

    prompt = f"""You are an IBM Cloud migration analyst.
Analyse this infrastructure description and extract key information.

Infrastructure data:
{raw}

Return a JSON object with exactly these fields:
{{
    "total_servers": <number>,
    "total_databases": <number>,
    "operating_systems": {{"Windows": <count>, "Linux": <count>}},
    "critical_applications": ["app1", "app2"],
    "complexity_score": <1-10 float>,
    "migration_pattern": "<rehost|replatform|refactor>",
    "migration_blockers": ["blocker1", "blocker2"]
}}

Complexity scoring:
- 1-3: Simple, few servers, standard OS
- 4-6: Medium, mixed OS, some legacy apps
- 7-9: Complex, many dependencies, legacy systems
- 10: Very complex, major blockers exist

Return ONLY the JSON object."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    summary = json.loads(response.choices[0].message.content)
    print(f"  [Agent 1] Done: {summary['total_servers']} servers, complexity {summary['complexity_score']}/10")

    return {**state, "infra_summary": summary, "current_node": "agent1"}

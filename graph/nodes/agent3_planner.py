"""
Agent 3 - Migration Planner
"""

import os
import json
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


class MigrationPhase(BaseModel):
    phase_number: int
    name: str
    duration_weeks: int
    ibm_services: List[str]
    activities: List[str]


class RiskItem(BaseModel):
    risk: str
    likelihood: str
    impact: str
    mitigation: str


class CostEstimate(BaseModel):
    current_annual_cost_usd: int
    ibm_cloud_annual_cost_usd: int
    migration_one_time_cost_usd: int
    three_year_saving_usd: int
    saving_percentage: float


class IBMArchitecture(BaseModel):
    compute: str
    database: str
    storage: str
    networking: str
    security: str
    monitoring: str


class MigrationPlanOutput(BaseModel):
    executive_summary: str = Field(min_length=50)
    phases: List[MigrationPhase] = Field(min_length=1)
    ibm_target_architecture: IBMArchitecture
    risk_register: List[RiskItem]
    compliance_checklist: List[str]
    cost_estimate: CostEstimate
    next_steps: List[str] = Field(min_length=3)


def agent3_plan(state: dict) -> dict:
    print("  [Agent 3] Writing migration plan...")

    summary = state.get("infra_summary", {})
    chunks = state.get("rag_chunks", [])
    client_name = state.get("client_name", "Client")

    ibm_context = "\n\n".join([
        f"[IBM Knowledge - {c['category']}]: {c['text']}"
        for c in chunks
    ])

    prompt = f"""You are an IBM Cloud migration expert writing a professional migration plan.

Client: {client_name}
Infrastructure Summary:
{json.dumps(summary, indent=2)}

IBM Knowledge Base (use ONLY these IBM services):
{ibm_context}

Write a complete IBM Cloud migration plan.
Use ONLY IBM services mentioned in the knowledge base.
Never mention AWS, Azure, or GCP.
Include specific costs, timelines, and IBM service names."""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an IBM Cloud migration expert. Only recommend IBM Cloud services."
            },
            {"role": "user", "content": prompt}
        ],
        response_format=MigrationPlanOutput
    )

    plan = completion.choices[0].message.parsed
    plan_dict = plan.model_dump()

    print(f"  [Agent 3] Plan written: {len(plan.phases)} phases, {len(plan.risk_register)} risks")

    return {
        **state,
        "migration_plan": plan_dict,
        "current_node": "agent3"
    }

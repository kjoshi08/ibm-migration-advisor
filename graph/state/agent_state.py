"""
Agent State — the memory of the entire pipeline
------------------------------------------------
This TypedDict travels through every node in the graph.
Each agent reads from it and writes back to it.
Senior engineers define state before writing any agent code.
"""

from typing import TypedDict, Optional, Literal


class InfrastructureSummary(TypedDict):
    total_servers: int
    total_databases: int
    operating_systems: dict
    critical_applications: list
    complexity_score: float        # 1-10
    migration_pattern: str         # rehost, replatform, refactor
    migration_blockers: list


class MigrationPhase(TypedDict):
    phase_number: int
    name: str
    duration_weeks: int
    ibm_services: list
    activities: list


class RiskItem(TypedDict):
    risk: str
    likelihood: str    # low, medium, high
    impact: str
    mitigation: str


class MigrationPlan(TypedDict):
    executive_summary: str
    phases: list
    ibm_target_architecture: dict
    risk_register: list
    compliance_checklist: list
    cost_estimate: dict
    next_steps: list


class EvalScores(TypedDict):
    rouge_l: float
    f1: float
    hallucination_rate: float
    judge_score: float
    passed: bool           # True if judge_score >= 7.0


class AgentState(TypedDict):
    # Input
    client_name: str
    file_path: str
    raw_infrastructure: str

    # Agent 1 output
    infra_summary: Optional[InfrastructureSummary]

    # Agent 2 output
    rag_chunks: Optional[list]
    retrieval_queries: Optional[list]

    # Agent 3 output
    migration_plan: Optional[MigrationPlan]

    # Quality control
    eval_scores: Optional[EvalScores]
    retry_count: int
    human_review_needed: bool

    # Routing
    current_node: str
    error: Optional[str]

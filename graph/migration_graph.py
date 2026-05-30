"""
LangGraph Migration Pipeline
------------------------------
State machine with conditional routing.
Not a fixed sequential pipeline — a smart graph
that makes decisions based on state.

Routing logic:
- Simple infra (complexity < 3) -> skip RAG -> plan directly
- Complex infra (complexity > 8) -> flag for human review
- Failed quality check -> retry retrieval (max 2 retries)
- All other cases -> full pipeline
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from graph.state.agent_state import AgentState
from graph.nodes.agent1_analyser import agent1_analyse
from graph.nodes.agent2_retriever import agent2_retrieve
from graph.nodes.agent3_planner import agent3_plan


def route_after_analysis(
    state: AgentState
) -> Literal["retrieve", "plan", "human_review"]:
    """
    Decide next step after Agent 1 analyses infrastructure.
    This is what makes it agentic — not just sequential.
    """
    complexity = state.get("infra_summary", {}).get("complexity_score", 5)

    if complexity > 8:
        print(f"  [Router] Complexity {complexity}/10 — flagging for human review")
        return "human_review"
    elif complexity < 3:
        print(f"  [Router] Complexity {complexity}/10 — simple, skipping RAG")
        return "plan"
    else:
        print(f"  [Router] Complexity {complexity}/10 — full pipeline")
        return "retrieve"


def route_after_quality(
    state: AgentState
) -> Literal["done", "retry", "human_review"]:
    """
    Decide what to do with the generated plan.
    """
    scores = state.get("eval_scores", {})
    retry_count = state.get("retry_count", 0)

    if not scores:
        return "done"

    if scores.get("passed", False):
        print(f"  [Router] Quality passed — delivering plan")
        return "done"
    elif retry_count >= 2:
        print(f"  [Router] Max retries reached — human review needed")
        return "human_review"
    else:
        print(f"  [Router] Quality failed — retrying (attempt {retry_count + 1})")
        return "retry"


def quality_check_node(state: AgentState) -> AgentState:
    """
    Evaluate the generated plan quality.
    Simple version — checks if plan has all required sections.
    """
    plan = state.get("migration_plan", {})

    has_phases = bool(plan.get("phases"))
    has_risks = bool(plan.get("risk_register"))
    has_costs = bool(plan.get("cost_estimate"))
    has_summary = len(plan.get("executive_summary", "")) > 50

    score = sum([has_phases, has_risks, has_costs, has_summary]) * 2.5
    passed = score >= 7.5

    print(f"  [Quality] Score: {score}/10 — {'PASSED' if passed else 'FAILED'}")

    return {
        **state,
        "eval_scores": {
            "rouge_l": 0.0,
            "f1": 0.0,
            "hallucination_rate": 0.0,
            "judge_score": score,
            "passed": passed
        },
        "retry_count": state.get("retry_count", 0) + (0 if passed else 1),
        "current_node": "quality_check"
    }


def human_review_node(state: AgentState) -> AgentState:
    """
    Flag plan for human review.
    In production: sends Slack notification to consultant.
    """
    print("  [Human Review] Plan flagged for consultant review")
    return {
        **state,
        "human_review_needed": True,
        "current_node": "human_review"
    }


def build_graph():
    """Build and compile the migration graph."""
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("analyse", agent1_analyse)
    graph.add_node("retrieve", agent2_retrieve)
    graph.add_node("plan", agent3_plan)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("human_review", human_review_node)

    # Entry point
    graph.set_entry_point("analyse")

    # Conditional routing after analysis
    graph.add_conditional_edges(
        "analyse",
        route_after_analysis,
        {
            "retrieve": "retrieve",
            "plan": "plan",
            "human_review": "human_review"
        }
    )

    # Fixed edges
    graph.add_edge("retrieve", "plan")
    graph.add_edge("plan", "quality_check")

    # Conditional routing after quality check
    graph.add_conditional_edges(
        "quality_check",
        route_after_quality,
        {
            "done": END,
            "retry": "retrieve",
            "human_review": "human_review"
        }
    )

    graph.add_edge("human_review", END)

    return graph.compile()


# Singleton graph instance
migration_graph = build_graph()

"""
MCP Server — IBM Migration Advisor
------------------------------------
Exposes the migration pipeline as an MCP tool.
Any AI agent (Claude, GPT, Cursor) can call this.
Standard protocol — not locked to one interface.

This is what "MCP-compatible" means on your resume.
"""

from mcp.server.fastmcp import FastMCP
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

mcp = FastMCP("IBM Migration Advisor")


@mcp.tool()
async def analyse_migration(
    client_name: str,
    infrastructure_description: str
) -> str:
    """
    Analyse a client infrastructure and generate
    an IBM Cloud migration plan with phases, costs,
    risks, and compliance requirements.

    Args:
        client_name: The client company name
        infrastructure_description: Description of servers,
            databases, and applications to migrate

    Returns:
        Complete IBM Cloud migration plan as text summary
    """
    from graph.migration_graph import migration_graph

    state = {
        "client_name": client_name,
        "file_path": "",
        "raw_infrastructure": infrastructure_description,
        "infra_summary": None,
        "rag_chunks": None,
        "retrieval_queries": None,
        "migration_plan": None,
        "eval_scores": None,
        "retry_count": 0,
        "human_review_needed": False,
        "current_node": "start",
        "error": None
    }

    result = migration_graph.invoke(state)
    plan = result.get("migration_plan", {})

    summary = f"""
IBM Cloud Migration Plan for {client_name}
{'='*50}

EXECUTIVE SUMMARY:
{plan.get('executive_summary', 'N/A')}

INFRASTRUCTURE:
- Servers: {result['infra_summary']['total_servers']}
- Databases: {result['infra_summary']['total_databases']}
- Complexity: {result['infra_summary']['complexity_score']}/10
- Pattern: {result['infra_summary']['migration_pattern']}

PHASES: {len(plan.get('phases', []))} phases planned
RISKS: {len(plan.get('risk_register', []))} risks identified
QUALITY SCORE: {result['eval_scores']['judge_score']}/10
"""
    return summary


@mcp.tool()
async def check_ibm_service(service_name: str) -> str:
    """
    Check if an IBM Cloud service name is real or hallucinated.

    Args:
        service_name: The IBM service name to validate

    Returns:
        Validation result with explanation
    """
    from safety.hallucination.detector import IBM_SERVICES_WHITELIST

    is_real = any(
        real.lower() in service_name.lower()
        for real in IBM_SERVICES_WHITELIST
    )

    if is_real:
        return f"✓ '{service_name}' is a valid IBM Cloud service."
    else:
        return f"✗ '{service_name}' is NOT a recognized IBM Cloud service. Possible hallucination."


if __name__ == "__main__":
    mcp.run(transport="stdio")

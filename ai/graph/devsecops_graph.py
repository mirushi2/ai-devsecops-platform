
from langgraph.graph import StateGraph, START, END

from ai.schemas import DevSecOpsState
from ai.agents.cicd_agent import run_cicd_agent
from ai.agents.security_agent import run_security_agent
from ai.agents.kubernetes_agent import run_kubernetes_agent


def cicd_node(state: DevSecOpsState) -> dict:
    result = run_cicd_agent(
        logs=state.get("jenkins_logs", "")
    )
    return {"cicd_result": result}


def security_node(state: DevSecOpsState) -> dict:
    result = run_security_agent(
        trivy_output=state.get("trivy_output", ""),
        pip_audit_output=state.get("pip_audit_output", ""),
        sonar_output=state.get("sonar_output", ""),
    )
    return {"security_result": result}


def kubernetes_node(state: DevSecOpsState) -> dict:
    result = run_kubernetes_agent(
        deployment_status=state.get("deployment_status", ""),
        pod_status=state.get("pod_status", ""),
        kubernetes_events=state.get("kubernetes_events", ""),
    )
    return {"kubernetes_result": result}


def format_retrieved_knowledge(result: dict) -> str:
    """Format Databricks AI Search documents for the final report."""

    documents = result.get("retrieved_knowledge", [])

    if not documents:
        return "No knowledge documents retrieved."

    lines = []

    for document in documents:
        lines.append(
            f"- {document.get('id', 'Unknown ID')}: "
            f"{document.get('title', 'Untitled')} "
            f"(Relevance score: {document.get('score', 'N/A')})"
        )

    return "\n".join(lines)


def format_retrieval_status(result: dict) -> str:
    """Show whether Databricks AI Search retrieval succeeded."""

    status = result.get("retrieval_status", "UNKNOWN")
    error = result.get("retrieval_error")

    if error:
        return f"{status} | Error: {error}"

    return status


def report_node(state: DevSecOpsState) -> dict:
    cicd = state.get("cicd_result", {})
    security = state.get("security_result", {})
    kubernetes = state.get("kubernetes_result", {})

    report = f"""
==================================================
       AI-DRIVEN DEVSECOPS ANALYSIS REPORT
==================================================

BUILD INFORMATION
Build Number: {state.get("build_number", "Not provided")}
Build Status: {state.get("build_status", "Not provided")}

--------------------------------------------------
1. CI/CD AGENT
--------------------------------------------------
Status: {cicd.get("status", "UNKNOWN")}
Failure Type: {cicd.get("failure_type", "UNKNOWN")}
Reason: {cicd.get("reason", "Not available")}

Databricks AI Search:
Retrieval Status: {format_retrieval_status(cicd)}

Retrieved Knowledge:
{format_retrieved_knowledge(cicd)}

AI Analysis:
{cicd.get("ai_analysis", "Not available")}

--------------------------------------------------
2. SECURITY AGENT
--------------------------------------------------
Status: {security.get("status", "UNKNOWN")}
Critical Findings: {security.get("critical_count", 0)}
High Findings: {security.get("high_count", 0)}
Reason: {security.get("reason", "Not available")}

Databricks AI Search:
Retrieval Status: {format_retrieval_status(security)}

Retrieved Knowledge:
{format_retrieved_knowledge(security)}

AI Analysis:
{security.get("ai_analysis", "Not available")}

--------------------------------------------------
3. KUBERNETES AGENT
--------------------------------------------------
Status: {kubernetes.get("status", "UNKNOWN")}
Failure Type: {kubernetes.get("failure_type", "UNKNOWN")}
Reason: {kubernetes.get("reason", "Not available")}

Databricks AI Search:
Retrieval Status: {format_retrieval_status(kubernetes)}

Retrieved Knowledge:
{format_retrieved_knowledge(kubernetes)}

AI Analysis:
{kubernetes.get("ai_analysis", "Not available")}

==================================================
                  END OF REPORT
==================================================
"""

    return {"final_report": report}


def build_devsecops_graph():
    """Build the complete three-agent workflow."""

    graph = StateGraph(DevSecOpsState)

    graph.add_node("cicd_agent", cicd_node)
    graph.add_node("security_agent", security_node)
    graph.add_node("kubernetes_agent", kubernetes_node)
    graph.add_node("report", report_node)

    graph.add_edge(START, "cicd_agent")
    graph.add_edge("cicd_agent", "security_agent")
    graph.add_edge("security_agent", "kubernetes_agent")
    graph.add_edge("kubernetes_agent", "report")
    graph.add_edge("report", END)

    return graph.compile()


devsecops_graph = build_devsecops_graph()

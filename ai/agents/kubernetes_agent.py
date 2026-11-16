
from typing import Any

from ai.llm.databricks_llm import ask_databricks
from ai.rag.retriever import retrieve_knowledge


def classify_kubernetes(
    deployment_status: str = "",
    pod_status: str = "",
    kubernetes_events: str = "",
) -> dict[str, Any]:
    """Classify Kubernetes deployment and pod health."""

    deployment = deployment_status.lower()
    pods = pod_status.lower()
    events = kubernetes_events.lower()

    if not any([
        deployment.strip(),
        pods.strip(),
        events.strip(),
    ]):
        return {
            "status": "UNKNOWN",
            "failure_type": "NO_DIAGNOSTICS",
            "reason": "No Kubernetes diagnostics were provided.",
        }

    combined = "\n".join([deployment, pods, events])

    checks = [
        (
            ["crashloopbackoff", "imagepullbackoff", "errimagepull"],
            "POD_FAILURE",
            "A pod is failing to start.",
        ),
        (
            ["oomkilled", "out of memory"],
            "RESOURCE_FAILURE",
            "A container may have exceeded its memory limit.",
        ),
        (
            ["failedscheduling", "insufficient cpu",
             "insufficient memory"],
            "SCHEDULING_FAILURE",
            "Kubernetes could not schedule a pod.",
        ),
        (
            ["progressdeadlineexceeded", "rollout failed",
             "deployment failed"],
            "DEPLOYMENT_FAILURE",
            "The deployment or rollout has failed.",
        ),
    ]

    for patterns, failure_type, reason in checks:
        if any(pattern in combined for pattern in patterns):
            return {
                "status": "FAILED",
                "failure_type": failure_type,
                "reason": reason,
            }

    if (
        "failed" in deployment
        or "failed" in pods
        or "error" in events
    ):
        return {
            "status": "FAILED",
            "failure_type": "GENERAL_FAILURE",
            "reason": "Kubernetes diagnostics contain failure indicators.",
        }

    if (
        ("healthy" in deployment or "ready" in deployment)
        and ("running" in pods or "ready" in pods)
    ):
        return {
            "status": "HEALTHY",
            "failure_type": "NONE",
            "reason": "Deployment and pod diagnostics indicate health.",
        }

    return {
        "status": "UNKNOWN",
        "failure_type": "UNCLASSIFIED",
        "reason": "Kubernetes health could not be determined.",
    }


def run_kubernetes_agent(
    deployment_status: str = "",
    pod_status: str = "",
    kubernetes_events: str = "",
) -> dict[str, Any]:
    """Analyse Kubernetes diagnostics using Databricks AI Search and LLM."""

    classification = classify_kubernetes(
        deployment_status,
        pod_status,
        kubernetes_events,
    )

    # Retrieve Kubernetes knowledge from Databricks.
    try:
        knowledge = retrieve_knowledge(
            query=(
                f"{classification['failure_type']} "
                f"{deployment_status[:1000]} "
                f"{pod_status[:1000]} "
                f"{kubernetes_events[:1000]}"
            ),
            category="Kubernetes",
            top_k=3,
        )
        retrieval_status = "SUCCESS"
        retrieval_error = None

    except Exception as exc:
        knowledge = []
        retrieval_status = "UNAVAILABLE"
        retrieval_error = type(exc).__name__

    prompt = f"""
You are a Kubernetes and Amazon EKS troubleshooting specialist.

DETERMINISTIC CLASSIFICATION:
{classification}

DEPLOYMENT STATUS:
{deployment_status[:4000]}

POD STATUS:
{pod_status[:4000]}

KUBERNETES EVENTS:
{kubernetes_events[:4000]}

RETRIEVED KNOWLEDGE FROM DATABRICKS AI SEARCH:
{knowledge}

Provide:
1. Root cause or likely cause.
2. Evidence from the supplied diagnostics.
3. Relevant retrieved troubleshooting knowledge.
4. Recommended troubleshooting steps.
5. Prevention recommendations.

Rules:
- Do not invent pod names, events, or error messages.
- Clearly distinguish confirmed facts from possible causes.
- Do not claim to have executed kubectl commands.
- Never recommend destructive cluster changes without explicit approval.
- Do not modify deployments or restart workloads.
- If no knowledge documents were retrieved, state that clearly.
"""

    try:
        explanation = ask_databricks(prompt)
        ai_status = "SUCCESS"

    except Exception as exc:
        explanation = (
            f"AI explanation unavailable: {type(exc).__name__}. "
            "Use the deterministic classification above."
        )
        ai_status = "UNAVAILABLE"

    return {
        **classification,
        "retrieved_knowledge": knowledge,
        "retrieval_status": retrieval_status,
        "retrieval_error": retrieval_error,
        "ai_status": ai_status,
        "ai_analysis": explanation,
    }

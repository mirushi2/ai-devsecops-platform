
from typing import Any

from ai.llm.databricks_llm import ask_databricks
from ai.rag.retriever import retrieve_knowledge


def classify_pipeline(logs: str) -> dict[str, Any]:
    """Classify pipeline status using deterministic checks."""

    if not logs or not logs.strip():
        return {
            "status": "UNKNOWN",
            "failure_type": "NO_LOGS",
            "reason": "No Jenkins logs were provided.",
        }

    text = logs.lower()

    checks = [
        (
            ["pytest failed", "test failures", "tests failed",
             "failed (", "error during test"],
            "TEST_FAILURE",
            "Automated tests failed.",
        ),
        (
            ["trivy scan failed", "vulnerabilities found",
             "security gate failed"],
            "SECURITY_GATE_FAILURE",
            "Security scanning or its policy gate failed.",
        ),
        (
            ["sonarqube quality gate failed", "quality gate failed"],
            "QUALITY_GATE_FAILURE",
            "SonarQube quality gate failed.",
        ),
        (
            ["deployment exceeded its progress deadline",
             "rollout failed", "deployment failed", "pods not ready"],
            "DEPLOYMENT_FAILURE",
            "Kubernetes deployment or rollout failed.",
        ),
        (
            ["build failed", "script returned exit code 1",
             "finished: failure"],
            "BUILD_FAILURE",
            "Jenkins reported a build failure.",
        ),
    ]

    for patterns, failure_type, reason in checks:
        if any(pattern in text for pattern in patterns):
            return {
                "status": "FAILED",
                "failure_type": failure_type,
                "reason": reason,
            }

    if "finished: success" in text or "build success" in text:
        return {
            "status": "SUCCESS",
            "failure_type": "NONE",
            "reason": "Jenkins reported a successful build.",
        }

    return {
        "status": "UNKNOWN",
        "failure_type": "UNCLASSIFIED",
        "reason": "No recognized pipeline result was found.",
    }


def run_cicd_agent(logs: str) -> dict[str, Any]:
    """Analyse CI/CD logs using Databricks AI Search and LLM."""

    classification = classify_pipeline(logs)

    # Retrieve troubleshooting knowledge from Databricks.
    try:
        knowledge = retrieve_knowledge(
            query=f"{classification['failure_type']} {logs[:1500]}",
            category="CI/CD",
            top_k=3,
        )
        retrieval_status = "SUCCESS"
        retrieval_error = None

    except Exception as exc:
        knowledge = []
        retrieval_status = "UNAVAILABLE"
        retrieval_error = type(exc).__name__

    prompt = f"""
You are a CI/CD troubleshooting specialist.

DETERMINISTIC CLASSIFICATION:
{classification}

JENKINS LOGS:
{logs[:12000]}

RETRIEVED KNOWLEDGE FROM DATABRICKS AI SEARCH:
{knowledge}

Provide:
1. Root cause or likely cause.
2. Evidence from the Jenkins logs.
3. Relevant retrieved troubleshooting knowledge.
4. Recommended troubleshooting steps.
5. Prevention recommendations.

Rules:
- Do not invent errors or log evidence.
- Distinguish confirmed facts from possible causes.
- Use retrieved knowledge when relevant.
- Do not claim to have executed commands.
- Never recommend bypassing security or quality gates.
- Keep the response concise and practical.
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

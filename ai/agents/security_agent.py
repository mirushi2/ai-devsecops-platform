
import re
from typing import Any

from ai.llm.databricks_llm import ask_databricks
from ai.rag.retriever import retrieve_knowledge


def classify_security(
    trivy_output: str = "",
    pip_audit_output: str = "",
    sonar_output: str = "",
) -> dict[str, Any]:
    """Classify security findings using deterministic checks."""

    combined = "\n".join([
        trivy_output,
        pip_audit_output,
        sonar_output,
    ])

    if not combined.strip():
        return {
            "status": "UNKNOWN",
            "critical_count": 0,
            "high_count": 0,
            "findings": [],
            "reason": "No security scan results were provided.",
        }

    critical_count = 0
    high_count = 0
    findings = []

    for line in combined.splitlines():
        critical_match = re.search(
            r"\bCRITICAL\s*:\s*(\d+)\b",
            line,
            re.IGNORECASE,
        )

        high_match = re.search(
            r"\bHIGH\s*:\s*(\d+)\b",
            line,
            re.IGNORECASE,
        )

        if critical_match:
            critical_count += int(critical_match.group(1))

        if high_match:
            high_count += int(high_match.group(1))

        if re.search(r"\b(CRITICAL|HIGH)\b", line, re.IGNORECASE):
            findings.append(line.strip())

    if critical_count > 0:
        status = "CRITICAL"
    elif high_count > 0:
        status = "HIGH"
    else:
        status = "REVIEW_REQUIRED"

    return {
        "status": status,
        "critical_count": critical_count,
        "high_count": high_count,
        "findings": findings,
        "reason": (
            "Explicit severity counts were found."
            if critical_count or high_count
            else "No explicit HIGH or CRITICAL counts were found. "
                 "This does not prove that the scans are clean."
        ),
    }


def run_security_agent(
    trivy_output: str = "",
    pip_audit_output: str = "",
    sonar_output: str = "",
) -> dict[str, Any]:
    """Analyse security results using Databricks AI Search and LLM."""

    classification = classify_security(
        trivy_output,
        pip_audit_output,
        sonar_output,
    )

    # Retrieve security knowledge from Databricks.
    try:
        knowledge = retrieve_knowledge(
            query=(
                f"{classification['status']} "
                f"{trivy_output[:1500]} "
                f"{pip_audit_output[:1500]} "
                f"{sonar_output[:1000]}"
            ),
            category="Security",
            top_k=3,
        )
        retrieval_status = "SUCCESS"
        retrieval_error = None

    except Exception as exc:
        knowledge = []
        retrieval_status = "UNAVAILABLE"
        retrieval_error = type(exc).__name__

    prompt = f"""
You are a DevSecOps security analysis specialist.

DETERMINISTIC CLASSIFICATION:
{classification}

TRIVY RESULTS:
{trivy_output[:6000]}

PIP-AUDIT RESULTS:
{pip_audit_output[:6000]}

SONARQUBE RESULTS:
{sonar_output[:6000]}

RETRIEVED KNOWLEDGE FROM DATABRICKS AI SEARCH:
{knowledge}

Provide:
1. Security risk summary.
2. Evidence from the supplied scan results.
3. Relevant retrieved troubleshooting knowledge.
4. Recommended remediation steps.
5. Prevention recommendations.

Rules:
- Never invent vulnerability IDs, package names, or CVEs.
- Distinguish confirmed findings from possible risks.
- Do not claim that a scan is clean when output is missing or incomplete.
- Never recommend suppressing or bypassing security gates.
- Do not execute remediation commands.
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

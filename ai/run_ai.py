
import json
import os
from pathlib import Path

from ai.graph.devsecops_graph import devsecops_graph


def load_ai_input() -> dict:
    """
    Load actual pipeline diagnostics from a JSON file.
    Use sample data only when no input file is supplied.
    """

    input_file = os.getenv("AI_INPUT_FILE")

    if input_file:
        path = Path(input_file)

        if not path.is_file():
            raise FileNotFoundError(
                f"AI input file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("AI input must be a JSON object.")

        return data

    print("No AI_INPUT_FILE supplied. Using local sample data.")

    return {
        "build_number": "LOCAL-001",
        "build_status": "FAILED",
        "jenkins_logs": """
        pytest failed: 2 tests failed
        Finished: FAILURE
        """,
        "trivy_output": """
        CRITICAL: 1
        HIGH: 2
        """,
        "pip_audit_output": "No known vulnerabilities found.",
        "sonar_output": "SonarQube quality gate passed.",
        "deployment_status": "Deployment status: healthy",
        "pod_status": """
        Pod application-001: Running
        Pod application-002: Running
        """,
        "kubernetes_events": "No warning events reported.",
    }


def main():
    print("\nStarting DevSecOps AI analysis...\n")

    ai_input = load_ai_input()

    result = devsecops_graph.invoke(ai_input)

    report = result.get("final_report", "No report generated.")

    print(report)

    report_file = os.getenv("AI_REPORT_FILE")

    if report_file:
        output_path = Path(report_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nAI report saved to: {output_path}")


if __name__ == "__main__":
    main()

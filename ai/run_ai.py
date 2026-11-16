
from ai.graph.devsecops_graph import devsecops_graph


def main():
    sample_input = {
        "build_number": "LOCAL-001",
        "build_status": "FAILED",

        "jenkins_logs": """
        Started by user
        Building application
        pytest failed: 2 tests failed
        Finished: FAILURE
        """,

        "trivy_output": """
        Trivy Security Scan Summary
        CRITICAL: 1
        HIGH: 2
        """,

        "pip_audit_output": """
        No known vulnerabilities found.
        """,

        "sonar_output": """
        SonarQube quality gate passed.
        """,

        "deployment_status": """
        Deployment status: healthy
        """,

        "pod_status": """
        Pod application-001: Running
        Pod application-002: Running
        """,

        "kubernetes_events": """
        No warning events reported.
        """,
    }

    print("\nStarting DevSecOps AI analysis...\n")

    result = devsecops_graph.invoke(sample_input)

    print(result["final_report"])


if __name__ == "__main__":
    main()

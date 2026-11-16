
from typing import TypedDict, Any


class DevSecOpsState(TypedDict, total=False):
    # Pipeline information
    build_number: str
    build_status: str
    jenkins_logs: str

    # Security scan information
    trivy_output: str
    pip_audit_output: str
    sonar_output: str

    # Kubernetes information
    deployment_status: str
    pod_status: str
    kubernetes_events: str

    # Agent results
    cicd_result: dict[str, Any]
    security_result: dict[str, Any]
    kubernetes_result: dict[str, Any]

    # Final report
    final_report: str
    errors: list[str]

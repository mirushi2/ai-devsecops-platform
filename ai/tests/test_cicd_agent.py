
from unittest.mock import patch

from ai.agents.cicd_agent import classify_pipeline, run_cicd_agent


def test_detect_test_failure():
    result = classify_pipeline("pytest failed: 2 tests failed")

    assert result["status"] == "FAILED"
    assert result["failure_type"] == "TEST_FAILURE"


def test_detect_security_failure():
    result = classify_pipeline("Trivy scan failed")

    assert result["failure_type"] == "SECURITY_GATE_FAILURE"


def test_detect_quality_gate_failure():
    result = classify_pipeline("SonarQube quality gate failed")

    assert result["failure_type"] == "QUALITY_GATE_FAILURE"


def test_detect_deployment_failure():
    result = classify_pipeline("deployment exceeded its progress deadline")

    assert result["failure_type"] == "DEPLOYMENT_FAILURE"


def test_detect_success():
    result = classify_pipeline("Finished: SUCCESS")

    assert result["status"] == "SUCCESS"


def test_empty_logs():
    result = classify_pipeline("")

    assert result["status"] == "UNKNOWN"


@patch("ai.agents.cicd_agent.ask_databricks")
def test_run_cicd_agent(mock_llm):
    mock_llm.return_value = "The test stage failed."

    result = run_cicd_agent("pytest failed: 2 tests failed")

    assert result["status"] == "FAILED"
    assert result["ai_status"] == "SUCCESS"
    assert result["ai_analysis"] == "The test stage failed."
    mock_llm.assert_called_once()


@patch("ai.agents.cicd_agent.ask_databricks")
def test_agent_handles_llm_failure(mock_llm):
    mock_llm.side_effect = RuntimeError("LLM unavailable")

    result = run_cicd_agent("Finished: SUCCESS")

    assert result["status"] == "SUCCESS"
    assert result["ai_status"] == "UNAVAILABLE"

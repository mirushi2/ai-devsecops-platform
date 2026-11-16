
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

from ai.config import (
    DATABRICKS_HOST,
    DATABRICKS_TOKEN,
    DATABRICKS_ENDPOINT,
    LLM_MAX_TOKENS,
    validate_databricks_config,
)


def ask_databricks(prompt: str) -> str:
    """
    Send a prompt to the configured Databricks serving endpoint
    and return the model's response.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    validate_databricks_config()

    client = WorkspaceClient(
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN,
    )

    message = ChatMessage(
        role=ChatMessageRole.USER,
        content=prompt,
    )

    response = client.serving_endpoints.query(
        name=DATABRICKS_ENDPOINT,
        messages=[message],
        max_tokens=LLM_MAX_TOKENS,
    )

    if not response.choices:
        raise RuntimeError("Databricks returned an empty response.")

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Databricks returned an empty message.")

    return content

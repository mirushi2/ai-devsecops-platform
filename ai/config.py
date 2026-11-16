
import os

from dotenv import load_dotenv

load_dotenv()

# Databricks authentication
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

# Databricks LLM endpoint
DATABRICKS_ENDPOINT = os.getenv(
    "DATABRICKS_ENDPOINT",
    "databricks-llama-4-maverick",
)

# Databricks AI Search configuration
AI_SEARCH_ENDPOINT = "devsecops-rag-endpoint"

AI_SEARCH_INDEX = (
    "workspace.devsecops.devsecops_knowledge_index"
)

# LLM configuration
LLM_MAX_TOKENS = 700


def validate_databricks_config() -> None:
    if not DATABRICKS_HOST:
        raise ValueError(
            "DATABRICKS_HOST is not configured. Check your .env file."
        )

    if not DATABRICKS_TOKEN:
        raise ValueError(
            "DATABRICKS_TOKEN is not configured. Check your .env file."
        )

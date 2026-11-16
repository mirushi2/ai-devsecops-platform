
import json

from databricks.sdk import WorkspaceClient

from ai.config import (
    DATABRICKS_HOST,
    DATABRICKS_TOKEN,
    AI_SEARCH_INDEX,
    validate_databricks_config,
)


def retrieve_knowledge(
    query: str,
    category: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve relevant troubleshooting documents
    directly from Databricks AI Search using hybrid search.
    """

    if not query or not query.strip():
        return []

    validate_databricks_config()

    client = WorkspaceClient(
        host=DATABRICKS_HOST,
        token=DATABRICKS_TOKEN,
    )

    filters_json = None

    if category:
        filters_json = json.dumps({
            "category": category
        })

    response = client.vector_search_indexes.query_index(
        index_name=AI_SEARCH_INDEX,
        columns=[
            "id",
            "category",
            "title",
            "content",
        ],
        query_text=query,
        query_type="HYBRID",
        filters_json=filters_json,
        num_results=max(1, min(top_k, 10)),
    )

    if not response.manifest or not response.result:
        return []

    column_names = [
        column.name
        for column in response.manifest.columns
    ]

    documents = []

    for row in response.result.data_array or []:
        document = dict(zip(column_names, row))
        documents.append(document)

    return documents

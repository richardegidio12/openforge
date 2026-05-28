"""
LLM Client — thin wrapper over the Anthropic SDK.

Deliberately thin: no LangChain, no LlamaIndex, no abstraction layers.
Direct SDK calls give us full control over prompts, tokens, and errors.
Decision documented in ADR-011.
"""

from __future__ import annotations

import json
import os

from ..metadata.models import TableSchema


MODEL = "claude-opus-4-5"
MAX_TOKENS = 1024


def _client():
    """Lazy-load Anthropic client. Fails fast with a clear message if key missing."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set.\n"
            "Export it before running with --docs:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def generate_table_docs(table: TableSchema, mock: bool = False) -> dict:
    """
    Generate human-readable descriptions for a table and its columns.

    Args:
        table: TableSchema with column stats and sample values.
        mock: If True, returns realistic-looking fake docs without calling the API.
              Use for demos and development when ANTHROPIC_API_KEY is unavailable.

    Returns a dict with keys:
        table_description: str
        columns: dict[column_name, description]
    """
    if mock:
        return _mock_docs(table)

    cols_info = "\n".join([
        f"  - {c.name} ({c.type}): "
        f"{c.null_count} nulls, "
        f"{c.distinct_count} distinct values, "
        f"samples: {', '.join(str(v) for v in c.sample_values[:3])}"
        for c in table.columns
    ])

    prompt = f"""You are a data documentation expert. Given a database table's metadata, write clear and concise descriptions.

Table name: {table.name}
Row count: {table.row_count:,}
Source file: {table.source_path}

Columns:
{cols_info}

Respond with a JSON object with exactly this shape:
{{
  "table_description": "One sentence describing what this table contains and its business purpose.",
  "columns": {{
    "column_name": "One sentence describing what this column represents."
  }}
}}

Be specific. Use the sample values and statistics to infer real-world meaning. Do not include any text outside the JSON object."""

    client = _client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    # Defensive: extract JSON block even if model adds surrounding text
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


# ---------------------------------------------------------------------------
# Mock mode — realistic fake docs, zero API calls
# ---------------------------------------------------------------------------

_MOCK_TABLE_DESCRIPTIONS = {
    "sales":       "Transactional sales records capturing order details, customer info, products sold, and revenue per order.",
    "orders":      "Customer purchase orders with status tracking, amounts, and fulfillment metadata.",
    "customers":   "Master record of all registered customers including contact details and segmentation attributes.",
    "products":    "Product catalog with pricing, categories, and inventory metadata.",
    "events":      "Raw clickstream and user interaction events for behavioral analysis.",
    "users":       "Registered user accounts with authentication metadata and profile attributes.",
    "sessions":    "Web session records linking user activity to device, channel, and time-on-site metrics.",
}

_MOCK_COLUMN_DESCRIPTIONS: dict[str, str] = {
    "order_id":       "Unique identifier for each sales order, used as the primary key.",
    "customer_id":    "Foreign key referencing the customer who placed the order.",
    "customer_name":  "Full name of the customer at the time the order was placed.",
    "product":        "Name of the product purchased in this order line.",
    "category":       "High-level product category used for grouping and reporting (e.g. Electronics, Furniture).",
    "quantity":       "Number of units ordered for this product line.",
    "unit_price":     "Price per unit in USD at the time of purchase, before any discounts.",
    "total_amount":   "Total order value in USD, calculated as quantity × unit_price.",
    "order_date":     "Date the order was placed by the customer (ISO 8601 format).",
    "region":         "Geographic sales region associated with the customer's shipping address.",
    "status":         "Current fulfillment status of the order (completed, pending, cancelled).",
    "id":             "Surrogate primary key — unique integer identifier for each row.",
    "created_at":     "Timestamp when the record was first inserted into the system.",
    "updated_at":     "Timestamp of the most recent update to this record.",
    "email":          "Customer's email address used for account login and communications.",
    "name":           "Full display name of the entity.",
    "description":    "Free-text description providing additional context about this record.",
    "price":          "Monetary value in USD.",
    "date":           "Calendar date relevant to this record.",
    "timestamp":      "Precise datetime with timezone when the event occurred.",
    "user_id":        "Foreign key referencing the user associated with this record.",
    "type":           "Categorical classification used to differentiate record subtypes.",
    "value":          "Numeric measurement or metric captured for this record.",
    "source":         "Origin system or channel that produced this record.",
    "country":        "ISO country code for the geographic location associated with this record.",
}


def _mock_docs(table: TableSchema) -> dict:
    """
    Generate plausible documentation without calling the API.
    Uses the table name and column names to pick realistic descriptions.
    Falls back to a generic description for unknown names.
    """
    table_desc = _MOCK_TABLE_DESCRIPTIONS.get(
        table.name.lower(),
        f"Dataset containing {table.row_count:,} records with {len(table.columns)} attributes, "
        f"sourced from {table.source_path.split('/')[-1] if table.source_path else 'an external file'}."
    )

    col_docs: dict[str, str] = {}
    for col in table.columns:
        key = col.name.lower()
        if key in _MOCK_COLUMN_DESCRIPTIONS:
            col_docs[col.name] = _MOCK_COLUMN_DESCRIPTIONS[key]
        else:
            # Derive a generic description from name + type + stats
            sample_hint = f" Sample values include: {', '.join(str(v) for v in col.sample_values[:2])}." if col.sample_values else ""
            null_hint = f" Contains {col.null_count} null value(s)." if col.null_count > 0 else ""
            col_docs[col.name] = (
                f"{col.name.replace('_', ' ').capitalize()} field of type {col.type} "
                f"with {col.distinct_count} distinct values.{sample_hint}{null_hint}"
            )

    return {"table_description": table_desc, "columns": col_docs}

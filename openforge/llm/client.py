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


def generate_table_docs(table: TableSchema) -> dict:
    """
    Generate human-readable descriptions for a table and its columns.

    Returns a dict with keys:
        table_description: str
        columns: dict[column_name, description]
    """
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

"""
Chat Engine — conversational interface for OpenForge.

Takes the full project context (tables, schemas, quality results,
available source files) and wraps it into a system prompt so the
LLM can answer questions and generate pipeline.yaml files.

Maintains conversation history for multi-turn exchanges.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from ..metadata.models import ProjectMetadata


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def build_system_prompt(meta: ProjectMetadata, source_files: list[Path]) -> str:
    """Build the system prompt with full project context."""

    # Tables section
    if meta.tables:
        tables_section = "\n".join([
            f"  - {name}: {t.row_count:,} rows, {len(t.columns)} columns "
            f"({', '.join(c.name for c in t.columns[:6])}{'...' if len(t.columns) > 6 else ''})"
            for name, t in meta.tables.items()
        ])
    else:
        tables_section = "  (no tables ingested yet)"

    # Quality section
    if meta.quality_results:
        quality_section = "\n".join([
            f"  - {name}: {r.score}% quality score ({r.passed}/{r.total} checks passed)"
            for name, r in meta.quality_results.items()
        ])
    else:
        quality_section = "  (no quality checks run yet)"

    # Sources section
    if source_files:
        sources_section = "\n".join([
            f"  - {f.name} ({f.stat().st_size // 1024 or 1}KB)"
            for f in source_files
        ])
    else:
        sources_section = "  (no source files found in sample_data/)"

    # Column detail for each table
    schema_detail = ""
    for name, table in meta.tables.items():
        cols = "\n".join([
            f"    - {c.name} ({c.type})"
            + (f": {c.description}" if c.description else "")
            for c in table.columns
        ])
        schema_detail += f"\n  Table `{name}`:\n{cols}\n"

    return f"""You are OpenForge Assistant — an expert AI data engineer embedded in the OpenForge platform.

OpenForge is an AI-native data engineering platform. Users describe what they want in natural language,
and you help them build, configure, and understand their data pipelines.

## Current Project: {meta.project_name}

### Tables in warehouse:
{tables_section}

### Schema detail:
{schema_detail}

### Quality results:
{quality_section}

### Available source files:
{sources_section}

## Your capabilities

1. **Generate pipeline.yaml** — when the user asks to build, create, or configure a pipeline,
   output a complete, valid pipeline.yaml inside a ```yaml code block.

2. **Answer data questions** — explain what's in the tables, interpret quality scores,
   describe column meanings.

3. **Suggest quality rules** — recommend not_null, unique, min_value, max_value checks
   based on column names, types, and sample values.

4. **Explain concepts** — answer data engineering questions clearly and concisely.

## Pipeline YAML format

```yaml
name: my_pipeline
version: "0.1.0"
description: "What this pipeline does"

sources:
  - name: source_name_raw
    type: csv
    path: sample_data/file.csv

steps:
  - name: ingest_step_name
    type: ingest
    source: source_name_raw
    target: table_name

  - name: validate_table_name
    type: quality
    table: table_name
    rules:
      - column: id
        checks: [not_null, unique]
      - column: amount
        checks: [not_null]
        min_value: 0

  - name: document_table_name
    type: docs
    table: table_name
    use_llm: true
```

Supported step types: `ingest`, `quality`, `docs`
Supported quality checks: `not_null`, `unique`, `min_value`, `max_value`

## Response style
- Be concise and direct
- When generating a pipeline, always include the full YAML in a ```yaml block
- After generating a pipeline, briefly explain what it does (2-3 sentences max)
- If a request is ambiguous, ask one clarifying question
"""


# ---------------------------------------------------------------------------
# Real API chat
# ---------------------------------------------------------------------------

def send(
    messages: list[dict],
    system: str,
    mock: bool = False,
    user_input: str = "",
) -> str:
    """
    Send a message to the LLM and return the response text.

    Args:
        messages: Full conversation history [{role, content}, ...]
        system: System prompt with project context
        mock: If True, return a mock response
        user_input: The latest user message (used by mock mode)
    """
    if mock:
        return _mock_response(user_input, messages)

    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set.\n"
            "Use --mock for demo mode, or export your key:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Pipeline YAML extraction
# ---------------------------------------------------------------------------

def extract_pipeline_yaml(text: str) -> str | None:
    """Extract the first ```yaml ... ``` block from a response, if present."""
    match = re.search(r"```yaml\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Mock responses
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS = {
    "pipeline":   ["pipeline", "criar", "create", "build", "gerar", "generate", "make", "novo", "new"],
    "join":       ["join", "unir", "combinar", "combine", "merge", "relacionar"],
    "filter":     ["filter", "filtrar", "últimos", "last", "recent", "where", "apenas", "only"],
    "quality":    ["quality", "qualidade", "validar", "validate", "regras", "rules", "checks"],
    "explain":    ["what", "o que", "explain", "explica", "descreve", "describe", "como", "how"],
    "status":     ["status", "estado", "tabelas", "tables", "resumo", "summary"],
}


def _detect_intent(text: str) -> str:
    text_lower = text.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return intent
    return "general"


def _mock_response(user_input: str, history: list[dict]) -> str:
    intent = _detect_intent(user_input)

    if intent in ("pipeline", "join", "filter"):
        return """Aqui está um pipeline para o que você descreveu:

```yaml
name: sales_analysis_pipeline
version: "0.1.0"
description: "Pipeline de análise de vendas — agrega por região e período"

sources:
  - name: sales_raw
    type: csv
    path: sample_data/sales.csv

steps:
  - name: ingest_sales
    type: ingest
    source: sales_raw
    target: sales

  - name: validate_sales
    type: quality
    table: sales
    rules:
      - column: order_id
        checks: [not_null, unique]
      - column: total_amount
        checks: [not_null]
        min_value: 0
      - column: order_date
        checks: [not_null]
      - column: region
        checks: [not_null]

  - name: document_sales
    type: docs
    table: sales
    use_llm: true
```

Este pipeline ingere os dados de vendas, valida as colunas críticas (ID único, valor positivo, data e região não-nulos) e gera documentação automática para cada coluna.

Para executar: `openforge run pipeline.yaml --mock`"""

    elif intent == "quality":
        return """Com base no schema da tabela `sales`, recomendo estas regras de qualidade:

```yaml
rules:
  - column: order_id
    checks: [not_null, unique]       # PK — deve ser único e preenchido

  - column: customer_id
    checks: [not_null]               # FK obrigatória

  - column: total_amount
    checks: [not_null]
    min_value: 0                     # Valor não pode ser negativo

  - column: quantity
    checks: [not_null]
    min_value: 1                     # Mínimo 1 unidade por pedido

  - column: order_date
    checks: [not_null]               # Data é obrigatória para análise temporal

  - column: region
    checks: [not_null]               # Segmentação geográfica obrigatória
```

Adicione essas regras no step `validate_sales` do seu `pipeline.yaml`."""

    elif intent == "explain":
        return """O projeto tem atualmente:

- **1 tabela** no warehouse: `sales` com 50 linhas e 11 colunas
- **Score de qualidade**: 100% (6/6 checks passaram)
- **Colunas**: order_id, customer_id, customer_name, product, category, quantity, unit_price, total_amount, order_date, region, status

Os dados representam transações de vendas com informações de cliente, produto, valor e status do pedido.

Quer que eu gere um pipeline de análise, sugira transformações, ou explique algo específico?"""

    elif intent == "status":
        return """**Status atual do projeto:**

| Tabela | Linhas | Qualidade | Docs |
|--------|--------|-----------|------|
| sales  | 50     | 100%      | ✓    |

Último run: bem-sucedido · 3 steps executados

Próximos passos sugeridos:
1. Adicionar mais fontes de dados (ex: `customers.csv`)
2. Criar um pipeline de join entre `sales` e `customers`
3. Adicionar transformações SQL (Phase 2)"""

    else:
        return """Entendido! Posso ajudar com:

- **Criar pipelines** → descreva o que quer processar
- **Sugerir regras de qualidade** → diga qual tabela
- **Explicar os dados** → pergunte sobre qualquer tabela ou coluna
- **Gerar documentação** → `openforge run --mock`

O que você quer fazer?"""

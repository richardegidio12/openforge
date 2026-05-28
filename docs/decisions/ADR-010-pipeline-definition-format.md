# ADR-010 — Pipeline Definition Format

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** Choosing how users define and configure pipelines in OpenForge.

---

## Context

Users need to define what data sources exist, what steps to run (ingest, validate, document), and what rules to apply. The format must be:

- Readable by humans without documentation
- Writeable by both humans and AI (prompt → pipeline YAML in Phase 2)
- Versionable in git
- Extensible without breaking changes

## Decision

**YAML files validated by Pydantic v2 models** (`PipelineDefinition`, `PipelineStep`, `PipelineSource`, `QualityCheck`).

Example:
```yaml
name: sales_pipeline
version: "0.1.0"
description: "Process raw sales data"

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
```

## Why YAML + Pydantic

| Requirement | How YAML + Pydantic satisfies it |
|-------------|----------------------------------|
| Human-readable | YAML is the industry standard for data pipeline config (Airflow DAGs, dbt project.yml, Dagster configs) |
| AI-writable | LLMs produce valid YAML reliably; Phase 2 prompt → YAML generation is straightforward |
| Validated | Pydantic catches schema errors at load time with clear error messages |
| Versionable | Plain text, perfect git diffs |
| Extensible | Add new fields to Pydantic models with `Optional` — backward compatible |

## Alternatives Rejected

| Alternative | Reason rejected |
|-------------|----------------|
| Python DSL (`pipeline = Pipeline(...)`) | Powerful but requires Python knowledge; harder for AI to generate; mixes config and code |
| JSON | Verbose, no comments, worse for human authoring |
| TOML | Good for simple config but awkward for nested structures (rules, steps) |
| HCL (Terraform style) | Unfamiliar to data engineers |
| Protobuf/Avro | Over-engineered for Phase 1; no human editing |

## Consequences

- **Positive:** `pipeline.yaml` can be committed alongside data code — pipeline-as-code
- **Positive:** Familiar to anyone who has used Airflow, dbt, or Kubernetes
- **Positive:** Phase 2 AI feature (`openforge chat` → generates pipeline.yaml) is straightforward
- **Tradeoff:** YAML indentation errors are annoying — mitigated by Pydantic's clear error messages
- **Future:** A JSON Schema will be generated from the Pydantic models for IDE autocomplete support

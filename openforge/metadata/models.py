"""
Pydantic models for the OpenForge metadata layer.

Everything flows through these models: schema inference output,
ingestion state, quality results, pipeline definitions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Schema models
# ---------------------------------------------------------------------------

class ColumnSchema(BaseModel):
    """Represents a single column in a table."""

    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None
    sample_values: list[Any] = Field(default_factory=list)
    null_count: int = 0
    distinct_count: Optional[int] = None


class TableSchema(BaseModel):
    """Represents a table — its shape, origin, and documentation."""

    name: str
    source_path: Optional[str] = None
    row_count: int = 0
    columns: list[ColumnSchema] = Field(default_factory=list)
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Quality models
# ---------------------------------------------------------------------------

class QualityCheck(BaseModel):
    """A set of validation rules for a single column."""

    column: str
    checks: list[str] = Field(default_factory=list)  # not_null, unique, min_value, max_value
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class QualityResult(BaseModel):
    """Aggregated result of all quality checks for a table."""

    table: str
    passed: int = 0
    failed: int = 0
    total: int = 0
    score: float = 0.0  # 0–100
    details: list[dict] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def passed_all(self) -> bool:
        return self.failed == 0


# ---------------------------------------------------------------------------
# Pipeline models
# ---------------------------------------------------------------------------

class PipelineSource(BaseModel):
    """A data source referenced in a pipeline."""

    name: str
    type: str  # csv, parquet, json
    path: str


class PipelineStep(BaseModel):
    """A single executable step inside a pipeline."""

    name: str
    type: str  # ingest | quality | docs | transform
    source: Optional[str] = None
    target: Optional[str] = None
    table: Optional[str] = None
    rules: Optional[list[QualityCheck]] = None
    use_llm: bool = False
    sql: Optional[str] = None


class ConnectorConfig(BaseModel):
    """
    Target connector configuration — declared in pipeline.yaml under `connector:`.

    If absent from the pipeline, DuckDB local warehouse is used by default.

    Note: `db_schema` maps to `schema` in pipeline.yaml via model_config alias.
    """

    model_config = {"populate_by_name": True}

    type: str = "duckdb"            # duckdb | trino | bigquery | snowflake
    # Trino
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    catalog: Optional[str] = None
    db_schema: Optional[str] = Field(None, alias="schema")   # `schema` is reserved in Pydantic
    http_scheme: Optional[str] = "http"
    password: Optional[str] = None
    # BigQuery
    project: Optional[str] = None
    dataset: Optional[str] = None
    credentials_path: Optional[str] = None
    # Snowflake
    account: Optional[str] = None
    warehouse: Optional[str] = None
    database: Optional[str] = None


class PipelineDefinition(BaseModel):
    """Full pipeline definition — loaded from pipeline.yaml."""

    name: str
    version: str = "0.1.0"
    description: Optional[str] = None
    connector: Optional[ConnectorConfig] = None   # None → defaults to DuckDB
    sources: list[PipelineSource] = Field(default_factory=list)
    steps: list[PipelineStep] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Project state (persisted to .openforge/metadata.json)
# ---------------------------------------------------------------------------

class RunLog(BaseModel):
    """A single pipeline run record."""

    pipeline: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    success: bool = False
    steps_run: int = 0


class ProjectMetadata(BaseModel):
    """Root object — the full state of an OpenForge project."""

    project_name: str
    version: str = "0.1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tables: dict[str, TableSchema] = Field(default_factory=dict)
    quality_results: dict[str, QualityResult] = Field(default_factory=dict)
    runs: list[RunLog] = Field(default_factory=list)

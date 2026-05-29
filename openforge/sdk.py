"""
OpenForge Python SDK — programmatic interface.

Use this when you want to drive OpenForge from Python code
instead of the CLI. Same agents, same metadata layer, same connectors.

Quick start:
    from openforge import OpenForge

    of = OpenForge()
    of.run("pipeline.yaml")
    print(of.tables.list())
    print(of.quality.get("sales").score)

Or use the functional API:
    from openforge.sdk import run, infer, status
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .metadata import store
from .metadata.models import (
    ProjectMetadata, TableSchema, QualityResult, PipelineDefinition
)


# ---------------------------------------------------------------------------
# Functional API (stateless helpers)
# ---------------------------------------------------------------------------

def run(
    pipeline_path: str = "pipeline.yaml",
    docs: bool = False,
    mock: bool = False,
) -> bool:
    """
    Execute a pipeline. Returns True if all steps passed.

    Example:
        from openforge.sdk import run
        success = run("pipeline.yaml", mock=True)
    """
    from .pipeline.runner import run as _run
    return _run(pipeline_path, use_llm=docs or mock, mock=mock)


def infer(source_path: str, table_name: Optional[str] = None) -> TableSchema:
    """
    Infer schema from a CSV/Parquet file.

    Example:
        from openforge.sdk import infer
        schema = infer("data/sales.csv")
        for col in schema.columns:
            print(col.name, col.type)
    """
    from .agents.schema import infer as _infer
    return _infer(source_path, table_name)


def status() -> ProjectMetadata:
    """
    Return full project metadata (tables, quality results, runs).

    Example:
        from openforge.sdk import status
        meta = status()
        print(meta.tables["sales"].row_count)
    """
    return store.load()


def inspect(table_name: str):
    """
    Return a full column profile for a table in the warehouse.

    Example:
        from openforge.sdk import inspect
        profile = inspect("sales")
        for col in profile.columns:
            print(col.name, col.null_pct)
    """
    from .agents.profiler import profile
    return profile(table_name)


def heal(table_name: Optional[str] = None):
    """
    Diagnose quality failures for a table and return a HealingReport.

    Example:
        from openforge.sdk import heal
        report = heal("sales")
        for p in report.proposals:
            print(p.column, p.severity, p.proposal)
    """
    from .agents.healer import analyze

    meta = store.load()
    if not meta.quality_results:
        raise ValueError("No quality results found. Run a pipeline first.")

    target = table_name or min(meta.quality_results, key=lambda t: meta.quality_results[t].score)
    result = meta.quality_results[target]
    schema = meta.tables[target]
    return analyze(result, schema)


# ---------------------------------------------------------------------------
# Object-oriented API (fluent, stateful)
# ---------------------------------------------------------------------------

class TableNamespace:
    """Access tables in the metadata store."""

    def list(self) -> list[str]:
        """Return names of all ingested tables."""
        return list(store.load().tables.keys())

    def get(self, name: str) -> TableSchema:
        """Return schema for a specific table."""
        meta = store.load()
        if name not in meta.tables:
            raise KeyError(f"Table '{name}' not found. Available: {list(meta.tables.keys())}")
        return meta.tables[name]

    def __iter__(self):
        return iter(store.load().tables.values())


class QualityNamespace:
    """Access quality results."""

    def list(self) -> list[str]:
        """Return tables that have quality results."""
        return list(store.load().quality_results.keys())

    def get(self, table_name: str) -> QualityResult:
        """Return quality result for a table."""
        meta = store.load()
        if table_name not in meta.quality_results:
            raise KeyError(f"No quality results for '{table_name}'.")
        return meta.quality_results[table_name]

    def summary(self) -> dict[str, float]:
        """Return {table: score} dict for all tables."""
        return {
            name: qr.score
            for name, qr in store.load().quality_results.items()
        }


class OpenForge:
    """
    Main SDK entry point — fluent interface to all OpenForge features.

    Example:
        from openforge import OpenForge

        of = OpenForge()
        of.run("pipeline.yaml", mock=True)

        print(of.tables.list())
        print(of.quality.summary())

        schema = of.schema.infer("data/sales.csv")
        profile = of.inspect("sales")
        report  = of.heal("sales")
    """

    def __init__(self, project_root: Optional[str] = None):
        self._root = Path(project_root) if project_root else None
        self.tables = TableNamespace()
        self.quality = QualityNamespace()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def run(
        self,
        pipeline_path: str = "pipeline.yaml",
        docs: bool = False,
        mock: bool = False,
    ) -> bool:
        """Execute a pipeline."""
        return run(pipeline_path, docs=docs, mock=mock)

    def inspect(self, table_name: str):
        """Profile a table — column stats, distributions, top values."""
        return inspect(table_name)

    def heal(self, table_name: Optional[str] = None):
        """Diagnose quality failures and return fix proposals."""
        return heal(table_name)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    class _SchemaNamespace:
        def infer(self, source_path: str, table_name: Optional[str] = None) -> TableSchema:
            return infer(source_path, table_name)

    schema = _SchemaNamespace()

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def status(self) -> ProjectMetadata:
        """Return full project state."""
        return status()

    def __repr__(self) -> str:
        try:
            meta = store.load()
            return (
                f"<OpenForge project='{meta.project_name}' "
                f"tables={len(meta.tables)} "
                f"version='{meta.version}'>"
            )
        except Exception:
            return "<OpenForge not initialized — run openforge init>"

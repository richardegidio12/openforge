"""
Ingestion Agent — loads files into the local DuckDB warehouse.

Reads from any source supported by DuckDB (CSV, Parquet, JSON),
writes to .openforge/warehouse.db as a named table.
Re-runnable: existing tables are replaced.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from ..metadata.models import TableSchema
from ..metadata.store import get_warehouse_path


def load(table_schema: TableSchema, warehouse_path: Path | None = None) -> int:
    """
    Load a file into the DuckDB warehouse.

    Args:
        table_schema: Schema produced by the Schema Agent (contains source_path and name).
        warehouse_path: Override warehouse location. Defaults to .openforge/warehouse.db.

    Returns:
        Actual row count loaded (used to update metadata).
    """
    wh = str(warehouse_path or get_warehouse_path())
    source = table_schema.source_path
    table = table_schema.name

    con = duckdb.connect(wh)
    try:
        con.execute(f"DROP TABLE IF EXISTS {table}")
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM '{source}'")
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        con.close()

    return count


def query(sql: str, warehouse_path: Path | None = None) -> list[dict]:
    """
    Run a SQL query against the warehouse and return dicts.
    Useful for quick inspection without a full DuckDB connection.
    """
    wh = str(warehouse_path or get_warehouse_path())
    con = duckdb.connect(wh)
    try:
        result = con.execute(sql)
        cols = [d[0] for d in result.description]
        return [dict(zip(cols, row)) for row in result.fetchall()]
    finally:
        con.close()

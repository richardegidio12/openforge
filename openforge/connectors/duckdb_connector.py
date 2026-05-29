"""
DuckDB Connector — local warehouse, zero configuration.

This is the default connector. All Phase 1-3 functionality runs here.
Wraps the existing .openforge/warehouse.db behaviour behind the
BaseConnector interface so the pipeline runner is connector-agnostic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from .base import BaseConnector
from ..metadata.store import get_warehouse_path


class DuckDBConnector(BaseConnector):
    """Local DuckDB connector — reads/writes .openforge/warehouse.db."""

    name = "duckdb"

    def __init__(self, warehouse_path: Path | None = None):
        self._path = str(warehouse_path or get_warehouse_path())
        self._con: duckdb.DuckDBPyConnection | None = None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _conn(self) -> duckdb.DuckDBPyConnection:
        if self._con is None:
            self._con = duckdb.connect(self._path)
        return self._con

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        result = self._conn().execute("SELECT 42").fetchone()
        return result[0] == 42

    def close(self) -> None:
        if self._con:
            self._con.close()
            self._con = None

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def table_exists(self, table_name: str) -> bool:
        count = self._conn().execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [table_name],
        ).fetchone()[0]
        return count > 0

    def get_column_names(self, table_name: str) -> list[str]:
        rows = self._conn().execute(f"DESCRIBE {table_name}").fetchall()
        return [r[0] for r in rows]

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_table_from_records(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        drop_if_exists: bool = True,
    ) -> int:
        if not records:
            return 0
        con = self._conn()
        if drop_if_exists:
            con.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Use DuckDB's ability to CREATE TABLE from a list of dicts
        import pandas as pd
        df = pd.DataFrame(records)
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        return len(records)

    def load_from_file(self, table_name: str, source_path: str, drop_if_exists: bool = True) -> int:
        """Fast path: load directly from file (avoids Python round-trip)."""
        con = self._conn()
        if drop_if_exists:
            con.execute(f"DROP TABLE IF EXISTS {table_name}")
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{source_path}'")
        return con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def execute(self, sql: str) -> list[tuple]:
        return self._conn().execute(sql).fetchall()

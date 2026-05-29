"""
Profiler Agent — generates detailed statistical profiles for DuckDB tables.

Used by `openforge inspect` to give a deep view into a table's
data distribution: min, max, avg, percentiles, top values, null rate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import duckdb

from ..metadata.store import get_warehouse_path


@dataclass
class ColumnProfile:
    """Detailed statistics for a single column."""

    name: str
    type: str
    row_count: int
    null_count: int
    null_pct: float
    distinct_count: int
    distinct_pct: float

    # Numeric stats (None for non-numeric columns)
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    avg_val: Optional[float] = None
    p25: Optional[float] = None
    p50: Optional[float] = None
    p75: Optional[float] = None

    # Categorical stats
    top_values: list[tuple[str, int]] = field(default_factory=list)  # [(value, count), ...]


@dataclass
class TableProfile:
    """Full profile of a table — all columns."""

    table: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile] = field(default_factory=list)


_NUMERIC_TYPES = {"INTEGER", "BIGINT", "DOUBLE", "FLOAT", "HUGEINT", "SMALLINT", "TINYINT", "DECIMAL"}


def profile(table_name: str, warehouse_path: Path | None = None) -> TableProfile:
    """
    Generate a full profile for a DuckDB table.

    Args:
        table_name: Name of the table in the warehouse.
        warehouse_path: Override warehouse location.

    Returns:
        TableProfile with per-column statistics.
    """
    wh = str(warehouse_path or get_warehouse_path())
    con = duckdb.connect(wh)

    try:
        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        describe = con.execute(f"DESCRIBE {table_name}").fetchall()

        columns = []
        for row in describe:
            col_name, col_type = row[0], row[1]
            col_profile = _profile_column(con, table_name, col_name, col_type, row_count)
            columns.append(col_profile)

    finally:
        con.close()

    return TableProfile(
        table=table_name,
        row_count=row_count,
        column_count=len(columns),
        columns=columns,
    )


def _profile_column(
    con: duckdb.DuckDBPyConnection,
    table: str,
    col_name: str,
    col_type: str,
    row_count: int,
) -> ColumnProfile:
    q = f'"{col_name}"'
    base_type = col_type.upper().split("(")[0].strip()

    null_count = con.execute(f"SELECT COUNT(*) FROM {table} WHERE {q} IS NULL").fetchone()[0]
    null_pct = round((null_count / row_count) * 100, 1) if row_count > 0 else 0.0

    distinct_count = con.execute(f"SELECT COUNT(DISTINCT {q}) FROM {table}").fetchone()[0]
    distinct_pct = round((distinct_count / row_count) * 100, 1) if row_count > 0 else 0.0

    col = ColumnProfile(
        name=col_name,
        type=col_type,
        row_count=row_count,
        null_count=null_count,
        null_pct=null_pct,
        distinct_count=distinct_count,
        distinct_pct=distinct_pct,
    )

    # Numeric stats
    if base_type in _NUMERIC_TYPES:
        try:
            stats = con.execute(f"""
                SELECT
                    MIN(TRY_CAST({q} AS DOUBLE)),
                    MAX(TRY_CAST({q} AS DOUBLE)),
                    AVG(TRY_CAST({q} AS DOUBLE)),
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY TRY_CAST({q} AS DOUBLE)),
                    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY TRY_CAST({q} AS DOUBLE)),
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY TRY_CAST({q} AS DOUBLE))
                FROM {table}
                WHERE {q} IS NOT NULL
            """).fetchone()
            col.min_val, col.max_val, col.avg_val, col.p25, col.p50, col.p75 = (
                _round(v) for v in stats
            )
        except Exception:
            pass

    # Top 5 values for all columns
    try:
        top = con.execute(f"""
            SELECT CAST({q} AS VARCHAR), COUNT(*) as cnt
            FROM {table}
            WHERE {q} IS NOT NULL
            GROUP BY 1
            ORDER BY cnt DESC
            LIMIT 5
        """).fetchall()
        col.top_values = [(str(r[0]), r[1]) for r in top]
    except Exception:
        pass

    return col


def _round(v) -> Optional[float]:
    if v is None:
        return None
    return round(float(v), 2)

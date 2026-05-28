"""
Schema Agent — infers table schema from CSV/Parquet files using DuckDB.

No LLM required. Pure SQL introspection via DuckDB's DESCRIBE.
Output is a fully typed TableSchema ready for the metadata store.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import duckdb

from ..metadata.models import ColumnSchema, TableSchema


SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".json", ".tsv"}


def infer(source_path: str, table_name: Optional[str] = None) -> TableSchema:
    """
    Infer schema from a local file.

    Args:
        source_path: Path to CSV, Parquet, or JSON file.
        table_name: Override for the derived table name. Defaults to file stem.

    Returns:
        TableSchema with columns, types, null counts, distinct counts, samples.
    """
    path = Path(source_path)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    name = table_name or _normalize_name(path.stem)
    con = duckdb.connect()

    try:
        describe = con.execute(f"DESCRIBE SELECT * FROM '{source_path}'").fetchall()
        row_count = con.execute(f"SELECT COUNT(*) FROM '{source_path}'").fetchone()[0]

        columns = []
        for row in describe:
            col_name, col_type = row[0], row[1]
            col = _profile_column(con, source_path, col_name, col_type)
            columns.append(col)

    finally:
        con.close()

    return TableSchema(
        name=name,
        source_path=str(path.absolute()),
        row_count=row_count,
        columns=columns,
    )


def _profile_column(con: duckdb.DuckDBPyConnection, path: str, col_name: str, col_type: str) -> ColumnSchema:
    """Profile a single column: nulls, distinct count, sample values."""
    quoted = f'"{col_name}"'

    null_count = con.execute(
        f"SELECT COUNT(*) FROM '{path}' WHERE {quoted} IS NULL"
    ).fetchone()[0]

    distinct_count = con.execute(
        f"SELECT COUNT(DISTINCT {quoted}) FROM '{path}'"
    ).fetchone()[0]

    # Up to 3 non-null sample values
    samples_raw = con.execute(
        f"SELECT DISTINCT {quoted} FROM '{path}' WHERE {quoted} IS NOT NULL LIMIT 3"
    ).fetchall()
    sample_values = [str(s[0]) for s in samples_raw]

    return ColumnSchema(
        name=col_name,
        type=col_type,
        nullable=null_count > 0,
        null_count=null_count,
        distinct_count=distinct_count,
        sample_values=sample_values,
    )


def _normalize_name(stem: str) -> str:
    """Convert file stem to a valid table name."""
    return stem.lower().replace("-", "_").replace(" ", "_").replace(".", "_")

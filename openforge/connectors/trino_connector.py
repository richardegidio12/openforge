"""
Trino Connector — distributed SQL engine.

Connects to a running Trino cluster via the official Python client.
Supports reading from and writing to any Trino catalog
(Hive, Iceberg, PostgreSQL, MySQL, S3/Parquet, Delta Lake, etc.).

Install:  pip install trino
Docs:     https://github.com/trinodb/trino-python-client

Configuration in pipeline.yaml:
  connector:
    type: trino
    host: localhost        # Trino coordinator host
    port: 8080             # default Trino port
    user: admin            # Trino user
    catalog: hive          # target catalog
    schema: default        # target schema
    http_scheme: http      # http or https
    password: ""           # optional — leave empty for no-auth

Write strategy:
  For small datasets (< 100K rows): batch INSERT via Python cursor.
  For large datasets: write to Parquet locally, then CREATE TABLE
  pointing at the file location (requires S3/HDFS — Phase 4+).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import BaseConnector


BATCH_SIZE = 1000  # rows per INSERT batch


@dataclass
class TrinoConfig:
    host: str = "localhost"
    port: int = 8080
    user: str = "admin"
    catalog: str = "hive"
    schema: str = "default"
    http_scheme: str = "http"
    password: str = ""
    # Extra kwargs forwarded to trino.dbapi.connect()
    extra: dict = field(default_factory=dict)


class TrinoConnector(BaseConnector):
    """Trino connector — wraps the official trino Python client."""

    name = "trino"

    def __init__(self, config: TrinoConfig):
        self.config = config
        self._con = None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _conn(self):
        if self._con is None:
            try:
                import trino
            except ImportError:
                raise ImportError(
                    "trino package not installed.\n"
                    "Run: pip install trino"
                )
            cfg = self.config
            kwargs: dict[str, Any] = dict(
                host=cfg.host,
                port=cfg.port,
                user=cfg.user,
                catalog=cfg.catalog,
                schema=cfg.schema,
                http_scheme=cfg.http_scheme,
                **cfg.extra,
            )
            if cfg.password:
                from trino.auth import BasicAuthentication
                kwargs["auth"] = BasicAuthentication(cfg.user, cfg.password)

            self._con = trino.dbapi.connect(**kwargs)
        return self._con

    def _cursor(self):
        return self._conn().cursor()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Ping the Trino coordinator with a trivial query."""
        cur = self._cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        return result[0] == 1

    def close(self) -> None:
        if self._con:
            try:
                self._con.close()
            except Exception:
                pass
            self._con = None

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def table_exists(self, table_name: str) -> bool:
        cfg = self.config
        cur = self._cursor()
        cur.execute(f"""
            SELECT COUNT(*) FROM {cfg.catalog}.information_schema.tables
            WHERE table_schema = '{cfg.schema}'
              AND table_name   = '{table_name}'
        """)
        return cur.fetchone()[0] > 0

    def get_column_names(self, table_name: str) -> list[str]:
        cur = self._cursor()
        cur.execute(f"DESCRIBE {self.config.catalog}.{self.config.schema}.{table_name}")
        return [row[0] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_table_from_records(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        drop_if_exists: bool = True,
    ) -> int:
        """
        Load records into Trino via DDL + batched INSERT.

        Strategy:
          1. Infer CREATE TABLE DDL from first record's types
          2. DROP TABLE IF EXISTS (if requested)
          3. INSERT in batches of BATCH_SIZE rows

        Limitation: suitable for datasets up to ~1M rows.
        For larger volumes use the Parquet/S3 path (Phase 4+).
        """
        if not records:
            return 0

        cfg = self.config
        full_name = f"{cfg.catalog}.{cfg.schema}.{table_name}"
        cur = self._cursor()

        # Build DDL from first row
        ddl_cols = ", ".join(
            f"{col} {_infer_trino_type(val)}"
            for col, val in records[0].items()
        )
        ddl = f"CREATE TABLE {full_name} ({ddl_cols})"

        if drop_if_exists:
            cur.execute(f"DROP TABLE IF EXISTS {full_name}")

        cur.execute(ddl)

        # Batch INSERT
        cols = list(records[0].keys())
        col_list = ", ".join(cols)
        inserted = 0

        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i : i + BATCH_SIZE]
            values_sql = ", ".join(
                "(" + ", ".join(_format_value(row[c]) for c in cols) + ")"
                for row in batch
            )
            cur.execute(f"INSERT INTO {full_name} ({col_list}) VALUES {values_sql}")
            inserted += len(batch)

        return inserted

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def execute(self, sql: str) -> list[tuple]:
        cur = self._cursor()
        cur.execute(sql)
        return cur.fetchall()

    # ------------------------------------------------------------------
    # Trino-specific helpers
    # ------------------------------------------------------------------

    def run_query(self, sql: str) -> list[dict]:
        """Execute SQL and return results as list of dicts."""
        cur = self._cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def list_tables(self) -> list[str]:
        """List all tables in the configured catalog.schema."""
        cfg = self.config
        rows = self.execute(
            f"SHOW TABLES FROM {cfg.catalog}.{cfg.schema}"
        )
        return [r[0] for r in rows]

    def list_catalogs(self) -> list[str]:
        return [r[0] for r in self.execute("SHOW CATALOGS")]

    def list_schemas(self, catalog: str | None = None) -> list[str]:
        cat = catalog or self.config.catalog
        return [r[0] for r in self.execute(f"SHOW SCHEMAS FROM {cat}")]


# ------------------------------------------------------------------
# Type helpers
# ------------------------------------------------------------------

def _infer_trino_type(value: Any) -> str:
    """Infer a Trino SQL type from a Python value."""
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return "DOUBLE"
    return "VARCHAR"


def _format_value(value: Any) -> str:
    """Format a Python value as a SQL literal for INSERT."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    # Escape single quotes
    return "'" + str(value).replace("'", "''") + "'"

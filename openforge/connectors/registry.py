"""
Connector Registry — factory that maps connector type strings to classes.

Called by the pipeline runner with the connector config from pipeline.yaml.
Returns a ready-to-use BaseConnector instance.

Usage:
    connector = get_connector({"type": "duckdb"})
    connector = get_connector({"type": "trino", "host": "...", ...})
"""

from __future__ import annotations

from pathlib import Path

from .base import BaseConnector
from .duckdb_connector import DuckDBConnector
from .trino_connector import TrinoConnector, TrinoConfig


def get_connector(config: dict | None, warehouse_path: Path | None = None) -> BaseConnector:
    """
    Instantiate and return a connector from a config dict.

    Args:
        config: Dict from pipeline.yaml `connector:` section.
                If None or missing `type`, defaults to DuckDB.
        warehouse_path: Override for DuckDB warehouse path.

    Returns:
        A concrete BaseConnector instance, NOT yet connected.
        Call test_connection() to verify before use.
    """
    if not config:
        return DuckDBConnector(warehouse_path)

    connector_type = config.get("type", "duckdb").lower().strip()

    if connector_type == "duckdb":
        return DuckDBConnector(warehouse_path)

    elif connector_type == "trino":
        trino_cfg = TrinoConfig(
            host=config.get("host", "localhost"),
            port=int(config.get("port", 8080)),
            user=config.get("user", "admin"),
            catalog=config.get("catalog", "hive"),
            schema=config.get("schema") or config.get("db_schema", "default"),
            http_scheme=config.get("http_scheme", "http"),
            password=config.get("password", ""),
        )
        return TrinoConnector(trino_cfg)

    elif connector_type == "bigquery":
        from .stubs import BigQueryConnector
        return BigQueryConnector(**config)

    elif connector_type == "snowflake":
        from .stubs import SnowflakeConnector
        return SnowflakeConnector(**config)

    else:
        available = "duckdb, trino, bigquery (stub), snowflake (stub)"
        raise ValueError(
            f"Unknown connector type: '{connector_type}'. "
            f"Available: {available}"
        )

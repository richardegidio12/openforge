"""
Connector layer — abstracts the target execution engine.

Supported:
  duckdb    Local DuckDB warehouse (default, zero config)
  trino     Trino distributed SQL engine
  bigquery  Google BigQuery          (Phase 4 — stub)
  snowflake Snowflake                (Phase 4 — stub)

Usage in pipeline.yaml:

  # Default (DuckDB, no config needed)
  connector:
    type: duckdb

  # Trino
  connector:
    type: trino
    host: localhost
    port: 8080
    user: admin
    catalog: hive
    schema: analytics
"""

from .registry import get_connector
from .base import BaseConnector

__all__ = ["get_connector", "BaseConnector"]

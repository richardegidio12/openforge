"""
Stub connectors — BigQuery and Snowflake placeholders for Phase 4.

These raise a clear NotImplementedError so users see exactly what's
coming, rather than a cryptic ImportError or silent failure.
"""

from __future__ import annotations

from typing import Any

from .base import BaseConnector


class BigQueryConnector(BaseConnector):
    """
    Google BigQuery connector — Phase 4.

    Config:
      connector:
        type: bigquery
        project: my-gcp-project
        dataset: my_dataset
        credentials_path: /path/to/service-account.json  # optional
    """

    name = "bigquery"

    def __init__(self, **kwargs):
        self._config = kwargs
        _not_implemented(self.name)

    def test_connection(self) -> bool:        _not_implemented(self.name)
    def close(self) -> None:                  pass
    def table_exists(self, t) -> bool:        _not_implemented(self.name)
    def get_column_names(self, t) -> list:    _not_implemented(self.name)
    def create_table_from_records(self, *a, **kw) -> int: _not_implemented(self.name)
    def execute(self, sql) -> list:           _not_implemented(self.name)


class SnowflakeConnector(BaseConnector):
    """
    Snowflake connector — Phase 4.

    Config:
      connector:
        type: snowflake
        account: myorg-myaccount
        user: my_user
        password: my_password
        warehouse: COMPUTE_WH
        database: MY_DB
        schema: PUBLIC
    """

    name = "snowflake"

    def __init__(self, **kwargs):
        self._config = kwargs
        _not_implemented(self.name)

    def test_connection(self) -> bool:        _not_implemented(self.name)
    def close(self) -> None:                  pass
    def table_exists(self, t) -> bool:        _not_implemented(self.name)
    def get_column_names(self, t) -> list:    _not_implemented(self.name)
    def create_table_from_records(self, *a, **kw) -> int: _not_implemented(self.name)
    def execute(self, sql) -> list:           _not_implemented(self.name)


def _not_implemented(name: str):
    raise NotImplementedError(
        f"The '{name}' connector is planned for Phase 4 and not yet implemented.\n"
        f"Track progress: https://github.com/richardegidio12/openforge/issues\n"
        f"Available now: duckdb, trino"
    )

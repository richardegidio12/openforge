"""
BaseConnector — abstract interface every connector must implement.

All connectors expose the same 5 operations so the Pipeline Runner
doesn't need to know which engine it's talking to.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Abstract base class for all OpenForge connectors."""

    name: str = "base"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify the connector can reach its target.
        Returns True on success, raises on failure.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Release any open connections or resources."""
        ...

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Return True if the table exists in the target."""
        ...

    @abstractmethod
    def get_column_names(self, table_name: str) -> list[str]:
        """Return column names for an existing table."""
        ...

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    @abstractmethod
    def create_table_from_records(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        drop_if_exists: bool = True,
    ) -> int:
        """
        Create a table and load records into it.

        Args:
            table_name: Target table name.
            records: List of row dicts (from DuckDB fetchall as dicts).
            drop_if_exists: Drop and recreate if table already exists.

        Returns:
            Number of rows inserted.
        """
        ...

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, sql: str) -> list[tuple]:
        """Run a SQL query and return raw rows."""
        ...

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "BaseConnector":
        return self

    def __exit__(self, *_) -> None:
        self.close()

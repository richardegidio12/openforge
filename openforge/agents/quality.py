"""
Quality Agent — runs declarative validation rules against DuckDB tables.

Rules are defined in pipeline.yaml under each quality step.
Currently supported checks: not_null, unique, min_value, max_value.
New checks can be added by extending _run_single_check().
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from ..metadata.models import QualityCheck, QualityResult
from ..metadata.store import get_warehouse_path


def run_checks(
    table_name: str,
    checks: list[QualityCheck],
    warehouse_path: Path | None = None,
) -> QualityResult:
    """
    Run all quality checks for a table.

    Args:
        table_name: Name of the DuckDB table to validate.
        checks: List of QualityCheck objects (one per column).
        warehouse_path: Override warehouse location.

    Returns:
        QualityResult with pass/fail counts, score, and per-rule details.
    """
    wh = str(warehouse_path or get_warehouse_path())
    con = duckdb.connect(wh)

    details: list[dict] = []
    passed = 0
    failed = 0

    try:
        for check in checks:
            for rule in check.checks:
                result = _run_single_check(con, table_name, check.column, rule, check)
                details.append(result)
                if result["status"] == "pass":
                    passed += 1
                elif result["status"] == "fail":
                    failed += 1
    finally:
        con.close()

    total = passed + failed
    score = round((passed / total) * 100, 1) if total > 0 else 100.0

    return QualityResult(
        table=table_name,
        passed=passed,
        failed=failed,
        total=total,
        score=score,
        details=details,
    )


def _run_single_check(
    con: duckdb.DuckDBPyConnection,
    table: str,
    column: str,
    rule: str,
    check: QualityCheck,
) -> dict:
    """Execute a single check and return a result dict."""
    base = {"table": table, "column": column, "rule": rule}

    try:
        quoted = f'"{column}"'

        if rule == "not_null":
            count = con.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {quoted} IS NULL"
            ).fetchone()[0]
            if count == 0:
                return {**base, "status": "pass", "message": "No null values found"}
            return {**base, "status": "fail", "message": f"{count} null value(s) found"}

        elif rule == "unique":
            total = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            distinct = con.execute(
                f"SELECT COUNT(DISTINCT {quoted}) FROM {table}"
            ).fetchone()[0]
            dupes = total - distinct
            if dupes == 0:
                return {**base, "status": "pass", "message": "All values are unique"}
            return {**base, "status": "fail", "message": f"{dupes} duplicate value(s) found"}

        elif rule == "min_value":
            if check.min_value is None:
                return {**base, "status": "skip", "message": "min_value not specified"}
            count = con.execute(
                f"SELECT COUNT(*) FROM {table} WHERE TRY_CAST({quoted} AS DOUBLE) < {check.min_value}"
            ).fetchone()[0]
            if count == 0:
                return {**base, "status": "pass", "message": f"All values >= {check.min_value}"}
            return {**base, "status": "fail", "message": f"{count} value(s) below {check.min_value}"}

        elif rule == "max_value":
            if check.max_value is None:
                return {**base, "status": "skip", "message": "max_value not specified"}
            count = con.execute(
                f"SELECT COUNT(*) FROM {table} WHERE TRY_CAST({quoted} AS DOUBLE) > {check.max_value}"
            ).fetchone()[0]
            if count == 0:
                return {**base, "status": "pass", "message": f"All values <= {check.max_value}"}
            return {**base, "status": "fail", "message": f"{count} value(s) above {check.max_value}"}

        else:
            return {**base, "status": "skip", "message": f"Unknown rule '{rule}'"}

    except Exception as e:
        return {**base, "status": "error", "message": str(e)}

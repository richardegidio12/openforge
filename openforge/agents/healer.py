"""
Healer Agent — classifies quality failures and proposes fixes.

Given a failed QualityResult and the corresponding TableSchema,
it classifies each failure into a category and generates a
human-readable proposal to resolve it.

Failure categories:
  null_violation   — column has nulls, rule says not_null
  duplicate_key    — column has duplicates, rule says unique
  range_violation  — values outside min/max bounds
  unknown          — unclassified failure
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..metadata.models import QualityResult, TableSchema

FailureCategory = Literal["null_violation", "duplicate_key", "range_violation", "unknown"]


@dataclass
class HealingProposal:
    """A single classified failure with a proposed fix."""

    column: str
    rule: str
    category: FailureCategory
    message: str          # original failure message
    diagnosis: str        # what's wrong in plain English
    proposal: str         # how to fix it
    severity: Literal["critical", "warning", "info"]


@dataclass
class HealingReport:
    """Full report for a table — all failures classified and proposed."""

    table: str
    quality_score: float
    proposals: list[HealingProposal]

    @property
    def critical_count(self) -> int:
        return sum(1 for p in self.proposals if p.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for p in self.proposals if p.severity == "warning")


def analyze(
    result: QualityResult,
    schema: TableSchema,
) -> HealingReport:
    """
    Analyze a failed QualityResult and produce a HealingReport.

    Args:
        result: The QualityResult with failed checks.
        schema: The TableSchema for column context (null counts, distinct, samples).

    Returns:
        HealingReport with one HealingProposal per failed check.
    """
    col_index = {c.name: c for c in schema.columns}
    proposals: list[HealingProposal] = []

    for detail in result.details:
        if detail["status"] != "fail":
            continue

        col_name = detail["column"]
        rule = detail["rule"]
        message = detail["message"]
        col = col_index.get(col_name)

        proposal = _classify_and_propose(col_name, rule, message, col, schema)
        proposals.append(proposal)

    return HealingReport(
        table=result.table,
        quality_score=result.score,
        proposals=proposals,
    )


def _classify_and_propose(
    col_name: str,
    rule: str,
    message: str,
    col,
    schema: TableSchema,
) -> HealingProposal:
    """Classify a single failure and generate a proposal."""

    if rule == "not_null":
        null_count = _extract_count(message)
        pct = round((null_count / schema.row_count) * 100, 1) if schema.row_count > 0 else 0
        severity = "critical" if pct > 10 else "warning"

        if pct <= 5:
            fix = (
                f"Low null rate ({pct}%). Consider using a default value or "
                f"filtering nulls at ingestion: add a `WHERE {col_name} IS NOT NULL` filter "
                f"in a transform step (Phase 2)."
            )
        else:
            fix = (
                f"High null rate ({pct}%). Investigate the source data — "
                f"check if `{col_name}` is truly mandatory or should be Optional. "
                f"If Optional, remove the `not_null` check from pipeline.yaml."
            )

        return HealingProposal(
            column=col_name, rule=rule, category="null_violation",
            message=message,
            diagnosis=f"`{col_name}` has {null_count} null value(s) ({pct}% of rows).",
            proposal=fix,
            severity=severity,
        )

    elif rule == "unique":
        dupe_count = _extract_count(message)
        severity = "critical"

        if col_name.lower() in ("id", "order_id", "customer_id", "product_id", "user_id"):
            fix = (
                f"`{col_name}` looks like a primary key — {dupe_count} duplicate(s) suggest "
                f"a data quality problem upstream. Investigate the source system "
                f"for duplicate generation. Add a dedup transform step."
            )
        else:
            fix = (
                f"{dupe_count} duplicate(s) in `{col_name}`. "
                f"If uniqueness is not truly required here, remove the `unique` check. "
                f"If it is, add deduplication logic before ingestion."
            )

        return HealingProposal(
            column=col_name, rule=rule, category="duplicate_key",
            message=message,
            diagnosis=f"`{col_name}` has {dupe_count} duplicate value(s).",
            proposal=fix,
            severity=severity,
        )

    elif rule in ("min_value", "max_value"):
        violation_count = _extract_count(message)
        pct = round((violation_count / schema.row_count) * 100, 1) if schema.row_count > 0 else 0
        severity = "warning" if pct < 5 else "critical"
        bound = "minimum" if rule == "min_value" else "maximum"
        bound_word = "below" if rule == "min_value" else "above"

        fix = (
            f"{violation_count} value(s) {bound_word} the expected {bound} ({pct}% of rows). "
            f"Options: (1) adjust the threshold in pipeline.yaml if the bound is too strict, "
            f"(2) add a filter to exclude these rows, or "
            f"(3) investigate the source for data entry errors."
        )

        return HealingProposal(
            column=col_name, rule=rule, category="range_violation",
            message=message,
            diagnosis=f"`{col_name}` has {violation_count} value(s) outside the expected range.",
            proposal=fix,
            severity=severity,
        )

    else:
        return HealingProposal(
            column=col_name, rule=rule, category="unknown",
            message=message,
            diagnosis=f"Unexpected failure in `{col_name}` ({rule}): {message}",
            proposal="Investigate the source data and review the rule configuration.",
            severity="warning",
        )


def _extract_count(message: str) -> int:
    """Extract the first integer from a failure message."""
    import re
    match = re.search(r"\d+", message)
    return int(match.group()) if match else 0

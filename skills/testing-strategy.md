# Skill: Testing Strategy for Data Platforms

> *Applied by: Data Engineer (05), Analytics Engineer (06), Pipeline Planner (04)*

---

## The core principle

**Testing data is different from testing application code. A function either returns the right value or it doesn't. Data can be technically correct and business-logically wrong at the same time.**

The goal of a data testing strategy is not 100% coverage. It's **trust**: stakeholders must be able to look at a number and not question whether it's correct.

> "An untested metric is a metric someone will get fired for trusting."

---

## The data testing pyramid

```
                    ┌──────────────┐
                    │  E2E / Recon │  ← Reconciliation against source
                    │   tests      │     (slow, expensive, few)
                  ┌─┴──────────────┴─┐
                  │  Integration     │  ← Pipeline end-to-end
                  │  tests           │     (medium, run on PR merge)
              ┌───┴──────────────────┴───┐
              │  Contract / schema tests  │  ← dbt tests, schema checks
              │                          │     (fast, run on every PR)
          ┌───┴──────────────────────────┴───┐
          │  Unit tests                       │  ← Pure functions: transforms,
          │                                   │     calculations (fastest, most)
          └───────────────────────────────────┘
```

Most teams do only contract tests (dbt tests). That is necessary but not sufficient. You also need unit tests on transformation logic and reconciliation against the source.

---

## Layer 1 — Unit tests (transformation logic)

Unit tests target pure functions — calculations, transformations, business rules — in isolation from infrastructure.

```python
# ✅ Every non-trivial transformation gets a unit test

# The function
def calculate_net_revenue(order_amount: Decimal, discount_amount: Decimal | None) -> Decimal:
    """Net revenue = order amount minus discount. Per data contract: never negative."""
    discount = discount_amount or Decimal("0")
    net = order_amount - discount
    if net < 0:
        raise ValueError(
            f"net_revenue ({net}) cannot be negative. "
            f"order_amount={order_amount}, discount_amount={discount_amount}. "
            f"Check discount data from ERP."
        )
    return net

# The tests — each test teaches a business rule
def test_net_revenue_standard_case():
    """Standard order with a discount."""
    assert calculate_net_revenue(Decimal("100"), Decimal("20")) == Decimal("80")

def test_net_revenue_no_discount_returns_full_amount():
    """Orders without discounts: net = gross."""
    assert calculate_net_revenue(Decimal("100"), None) == Decimal("100")

def test_net_revenue_full_discount_returns_zero():
    """100% discount is valid (promotional orders)."""
    assert calculate_net_revenue(Decimal("100"), Decimal("100")) == Decimal("0")

def test_net_revenue_raises_on_discount_exceeding_amount():
    """Discount > order amount is an ERP data error, not a valid state."""
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_net_revenue(Decimal("50"), Decimal("80"))
```

**What gets unit tested:**
- Revenue calculations
- Date/period logic (fiscal year, week numbering)
- Status mappings (ERP codes → semantic statuses)
- Deduplication logic
- PII anonymization functions

**What does NOT get unit tested:**
- Infrastructure (GCS writes, BigQuery loads) — that's integration testing
- SQL in dbt — tested via dbt tests

---

## Layer 2 — Contract / schema tests (dbt tests)

These tests run on every PR and enforce the data contract. They are the most important automated safety net for data quality.

```yaml
# schema.yml

models:
  - name: fct_orders
    description: "Fact table. Grain: one row per order_id."
    columns:
      - name: order_id
        description: "Unique order identifier from ERP."
        tests:
          - not_null
          - unique           # if this fails, dedup in Silver has a bug

      - name: order_status
        tests:
          - not_null
          - accepted_values:
              values: ['completed', 'cancelled', 'pending', 'refunded']
              # if a new ERP status appears, this test catches it before Gold is wrong

      - name: net_revenue_brl
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "net_revenue_brl >= 0"
              # data contract rule: never negative

      - name: order_date
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "order_date >= '2020-01-01'"
              # sanity check: no orders before company was founded

    tests:
      # Business rule: net revenue never exceeds gross amount
      - dbt_utils.expression_is_true:
          expression: "net_revenue_brl <= order_amount_brl"
          name: net_revenue_never_exceeds_gross_amount

      # Referential integrity: every seller_id in fct_orders exists in dim_sellers
      - dbt_utils.relationships_where:
          to: ref('dim_sellers')
          field: seller_id
          from_condition: "seller_id IS NOT NULL"
```

### Test severity levels
Not all test failures are equal. Use `severity` to distinguish blocking failures from warnings:

```yaml
tests:
  - dbt_utils.recency:
      datepart: day
      field: order_date
      interval: 1
      severity: error    # blocks deploy — Gold cannot be stale

  - dbt_utils.expression_is_true:
      expression: "COUNT(*) > 100"
      severity: warn     # alerts but doesn't block — could be a slow day
```

---

## Layer 3 — Integration tests (pipeline end-to-end)

Integration tests run the full pipeline on a controlled dataset and verify the output meets expectations.

```python
# tests/integration/test_orders_pipeline.py

@pytest.fixture
def sample_erp_orders():
    """10 controlled orders with known expected outputs."""
    return [
        {"order_id": "ORD-001", "amount": 100.00, "discount": 20.00, "status": "completed"},
        {"order_id": "ORD-001", "amount": 100.00, "discount": 20.00, "status": "completed"},  # duplicate
        {"order_id": "ORD-002", "amount": 50.00, "discount": None, "status": "cancelled"},
        # ... 8 more
    ]

def test_orders_silver_deduplicates_erp_duplicates(sample_erp_orders, bq_test_client):
    """ERP sends duplicates. Silver must keep exactly one record per order_id."""
    run_silver_orders_pipeline(sample_erp_orders, dataset="test_silver")

    result = bq_test_client.query(
        "SELECT COUNT(*) as cnt FROM test_silver.orders WHERE order_id = 'ORD-001'"
    ).scalar()

    assert result == 1, f"Expected 1 row for ORD-001, got {result}. Dedup logic broken."

def test_orders_silver_removes_customer_cpf(sample_erp_orders, bq_test_client):
    """PII contract: customer_cpf must not exist in Silver."""
    run_silver_orders_pipeline(sample_erp_orders, dataset="test_silver")

    columns = bq_test_client.get_table_schema("test_silver.orders")
    assert "customer_cpf" not in columns, "PII violation: customer_cpf found in Silver."
```

**When to run:**
- On PR merge to `dev` branch (before staging deploy)
- Nightly on production data snapshot

---

## Layer 4 — Reconciliation tests (source of truth validation)

The highest-value and highest-cost test. Compares Gold output against the authoritative source.

```sql
-- reconciliation/monthly_revenue_check.sql
-- Run at end of month. Tolerance: 0.5% per data contract.

WITH erp_total AS (
  -- Direct query to ERP (or its replica)
  SELECT SUM(amount - COALESCE(discount, 0)) AS erp_net_revenue
  FROM erp_replica.orders
  WHERE order_date BETWEEN '2024-04-01' AND '2024-04-30'
    AND status = 'completed'
),
gold_total AS (
  SELECT SUM(net_revenue_brl) AS gold_net_revenue
  FROM gold.fct_orders
  WHERE order_month = '2024-04'
    AND is_completed = true
)
SELECT
  erp_net_revenue,
  gold_net_revenue,
  ABS(erp_net_revenue - gold_net_revenue) / erp_net_revenue AS divergence_pct,
  divergence_pct <= 0.005 AS within_slo   -- 0.5% tolerance
FROM erp_total, gold_total
```

**When to run:**
- Monthly, automated
- After any significant data backfill
- When stakeholders report number discrepancies

---

## Regression tests — preventing silent regressions

Reference queries with known expected results. If a dbt refactor or upstream change silently breaks a calculation, this catches it.

```python
# tests/regression/test_known_results.py
# These numbers were validated by the data owner (Carolina Mendes) on 2024-03-01.

KNOWN_RESULTS = [
    {
        "description": "Total completed orders in January 2024",
        "query": "SELECT COUNT(*) FROM gold.fct_orders WHERE order_month='2024-01' AND is_completed",
        "expected": 42_891,
        "tolerance_pct": 0.001,  # reconciliation already passed, this is regression-only
    },
    {
        "description": "Net revenue for top seller in Q1 2024",
        "query": """
            SELECT SUM(net_revenue_brl) FROM gold.fct_orders f
            JOIN gold.dim_sellers s ON f.seller_id = s.seller_id
            WHERE s.seller_name = 'Carlos Oliveira' AND order_quarter = '2024-Q1'
        """,
        "expected": 287_450.00,
        "tolerance_pct": 0.005,
    },
]

@pytest.mark.parametrize("case", KNOWN_RESULTS)
def test_known_result(case, bq_client):
    result = bq_client.query(case["query"]).scalar()
    divergence = abs(result - case["expected"]) / case["expected"]
    assert divergence <= case["tolerance_pct"], (
        f"Regression detected: '{case['description']}'\n"
        f"Expected: {case['expected']}, Got: {result}, Divergence: {divergence:.3%}"
    )
```

---

## CI/CD integration

```yaml
# .github/workflows/data-pipeline-ci.yml

on:
  pull_request:
    paths:
      - 'dbt/**'
      - 'dagster/**'
      - 'tests/**'

jobs:
  test:
    steps:
      - name: Unit tests
        run: pytest tests/unit/ -v --tb=short

      - name: dbt compile + schema tests (modified models only)
        run: |
          dbt compile
          dbt test --select state:modified+

      - name: Integration tests (on PR to main only)
        if: github.base_ref == 'main'
        run: pytest tests/integration/ -v --tb=short

  # Regression tests run nightly, not on every PR (too slow)
```

---

## Testing anti-patterns

| Anti-pattern | Problem | Fix |
|-------------|---------|-----|
| Testing only `not_null` | Catches missing data, misses wrong data | Add accepted_values + business logic tests |
| No unit tests on calculations | Revenue formula changes silently | Every calculation function gets unit tests |
| Integration tests in production | Risk of corrupting real data | Use a `test_` dataset in the same DW |
| Regression tests that never fail | Nobody updates the expected values | Review expected values quarterly |
| `severity: warn` on everything | Warnings become noise, nobody reads them | Use `warn` sparingly, `error` for contract violations |

---

## Quick reference: testing checklist per story

Before marking any story as done:
- [ ] Unit tests for every transformation function with non-trivial logic
- [ ] dbt tests: not_null + unique on PKs, accepted_values on status fields
- [ ] dbt tests: at least one business logic expression test per model
- [ ] Integration test if story modifies existing pipeline behavior
- [ ] Regression test entries if story changes a number stakeholders track
- [ ] All tests pass in CI before merge
- [ ] Test names describe the business rule, not just what they test

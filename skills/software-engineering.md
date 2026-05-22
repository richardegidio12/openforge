# Skill: Software Engineering for Data Platforms

> *This skill is applied by all technical personas: Data Architect (02), Pipeline Planner (04), Data Engineer (05), and Analytics Engineer (06).*

---

## The core principle

**A LLM can hold 10x more complexity in context than a human engineer can maintain under pressure at 2am.**

This skill exists to prevent that gap from becoming technical debt. Every technical decision — architecture, code, model, test — must be evaluated not just for correctness, but for **human maintainability**.

> "The best code for a data platform is the most boring code that solves the problem."

---

## The human comprehension test

Before producing any technical output, ask:

1. **The 2am test** — if this pipeline fails at 2am and a junior engineer is on-call, can they understand what broke and why within 10 minutes?
2. **The 6-month test** — if the engineer who wrote this leaves and someone new picks it up in 6 months, how long to get productive?
3. **The explain-aloud test** — can you explain what this code does in one sentence without using the word "basically"?

If any answer is "no" or "difficult", simplify before shipping.

---

## Principles

### 1. Boring over clever

```python
# ❌ Clever — technically correct, humanly expensive
result = {k: v for d in [base, overrides] for k, v in d.items() if v is not None}

# ✅ Boring — costs 3 more lines, saves 3 minutes every time someone reads it
result = base.copy()
for key, value in overrides.items():
    if value is not None:
        result[key] = value
```

The clever version requires the reader to decode it. The boring version explains itself. At scale, across a codebase, the clever version accumulates into an unmaintainable system.

---

### 2. Names that explain intent, not mechanics

```python
# ❌ Describes what the code does
def process_data(df):
def transform_rows(input):
def run_etl():

# ✅ Describes what the business concept is
def anonymize_customer_pii(raw_orders: DataFrame) -> DataFrame:
def calculate_net_revenue(order_amount, discount_amount) -> Decimal:
def ingest_erp_orders_incrementally(since: datetime) -> None:
```

In dbt:
```sql
-- ❌ Technical name, no context
{{ ref('stg_ord_cln_v2') }}

-- ✅ Self-documenting
{{ ref('stg_orders_with_pii_removed') }}
```

---

### 3. One function, one responsibility

A function that does two things is a function that's hard to test, hard to name, and hard to change without side effects.

```python
# ❌ Ingests AND transforms AND writes — can't test any part in isolation
def run_orders_pipeline(conn, gcs_client, bq_client):
    rows = conn.execute("SELECT * FROM orders WHERE updated_at > %s", [watermark])
    cleaned = [(r['id'], r['amount'] - r.get('discount', 0)) for r in rows]
    gcs_client.upload(cleaned)
    bq_client.load(cleaned)

# ✅ Each step is isolated, testable, and named
def fetch_new_orders(conn, since: datetime) -> list[RawOrder]:
    ...

def calculate_net_revenue(orders: list[RawOrder]) -> list[ProcessedOrder]:
    ...

def write_to_bronze(orders: list[ProcessedOrder], gcs_client) -> str:
    ...
```

---

### 4. Complexity budget

Every abstraction, every utility function, every shared macro costs cognitive load to understand. Abstractions must earn their place by being used at least 3 times and by making the call site clearer.

```sql
-- ❌ Macro that saves 2 lines but requires the reader to look up what it does
{{ apply_standard_cleaning(ref('stg_orders'), surrogate_key=['order_id'], dedup_by='updated_at') }}

-- ✅ Explicit — a new reader understands without jumping to the macro definition
SELECT
    {{ dbt_utils.generate_surrogate_key(['order_id']) }} AS order_sk,
    order_id,
    order_date,
    ...
FROM {{ ref('stg_orders') }}
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1
```

Use macros when the same pattern appears in 3+ models. Not before.

---

### 5. Error messages for humans

```python
# ❌ Error that only makes sense to the person who wrote the code
raise ValueError("Invalid state")
raise Exception("Pipeline failed")

# ✅ Error that tells the on-call engineer exactly what happened and what to check
raise ValueError(
    f"Order {order_id} has net_revenue ({net_revenue}) > order_amount ({order_amount}). "
    f"This violates the data contract. Check for discount calculation bugs in "
    f"silver.orders or upstream ERP data for batch {batch_id}."
)
```

---

### 6. Comments explain WHY, not WHAT

```python
# ❌ Describes what the code obviously does
# Loop through orders and remove duplicates
seen = set()
deduped = [o for o in orders if o['id'] not in seen and not seen.add(o['id'])]

# ✅ Explains why this decision was made
# ERP has a known bug that generates duplicate order_id on concurrent saves.
# We keep the most recent record by ingestion timestamp.
# See: pipeline-spec.md HIST-004, risk documented in architecture-document ADR-001.
orders_sorted = sorted(orders, key=lambda o: o['_ingested_at'], reverse=True)
seen_ids = set()
deduped = []
for order in orders_sorted:
    if order['id'] not in seen_ids:
        deduped.append(order)
        seen_ids.add(order['id'])
```

---

### 7. Scale for 10x, not 100x

Design decisions should anticipate realistic growth, not theoretical maximums.

| Decision | ❌ Over-engineered | ✅ Calibrated |
|----------|-------------------|---------------|
| Partitioning | Partition by hour from day 1 for a daily batch | Partition by day — matches your ingestion cadence |
| Parallelism | Distributed processing for 2k records/day | Single-threaded with async I/O if needed |
| Schema evolution | Full schema registry + Avro + compatibility checks | dbt `schema.yml` + CI tests on column changes |
| Caching | Redis cluster for query results | BigQuery slot reservation only when proven necessary |

The question is not "will this scale to 100x?" but "does this prevent 10x from being possible?" If the answer is no, the simpler solution wins.

---

### 8. Tests as the second reader

Tests are not just safety nets — they are documentation for the next engineer. A test that says `assert result is not None` tells nothing. A test that says what the business rule is teaches the reader.

```python
# ❌ Tests existence, not meaning
def test_net_revenue():
    result = calculate_net_revenue(100, 20)
    assert result is not None
    assert result > 0

# ✅ Tests the business rule and teaches it
def test_net_revenue_subtracts_discount_from_order_amount():
    """Net revenue is order amount minus discount. Never negative."""
    assert calculate_net_revenue(order_amount=100, discount_amount=20) == 80

def test_net_revenue_treats_null_discount_as_zero():
    """Orders without discounts have net_revenue equal to order_amount."""
    assert calculate_net_revenue(order_amount=100, discount_amount=None) == 100

def test_net_revenue_cannot_exceed_order_amount():
    """A discount cannot create revenue above the original order amount."""
    with pytest.raises(ValueError, match="net_revenue cannot exceed order_amount"):
        calculate_net_revenue(order_amount=50, discount_amount=-30)
```

---

### 9. Idempotency and observability from day 1

These are not "nice to haves" to add later. They are load-bearing structural decisions.

**Idempotency** — running the same job twice must produce the same result, not double the data:
```python
# ❌ Append-only — re-running duplicates data
bq_client.load_table(data, table, write_disposition="WRITE_APPEND")

# ✅ Idempotent — re-running is safe
bq_client.load_table(data, table, write_disposition="WRITE_TRUNCATE")
# or for incremental: use MERGE with order_id as the unique key
```

**Observability** — every asset must emit enough metadata to be diagnosed without access to the source:
```python
# Minimum metadata on every Bronze write
metadata = {
    "_ingested_at": datetime.utcnow().isoformat(),
    "_source": "erp_tiny",
    "_batch_id": batch_id,
    "_record_count": len(records),
    "_watermark_used": str(watermark),
}
```

---

### 10. The LLM trap — a note for AI-assisted development

When using an LLM (including this Agent) to generate code, the LLM will tend toward:
- Comprehensive solutions that handle every edge case
- Clever abstractions that reduce repetition at the cost of readability
- Correct code that is longer than necessary to maintain

**The right posture:** treat LLM output as a first draft from a very senior engineer who doesn't know your team's cognitive capacity. Review every suggestion against the human comprehension test. Push back with: *"make this simpler — what's the version a mid-level engineer would write without needing to Google anything?"*

---

## Quick reference checklist

Before shipping any technical output (code, architecture decision, dbt model, pipeline spec):

- [ ] The 2am test: junior on-call can diagnose a failure in < 10 min?
- [ ] Names explain business intent, not technical mechanics
- [ ] Each function/asset/model does exactly one thing
- [ ] Abstractions are used 3+ times before being created
- [ ] Error messages include context (what failed, where, what to check)
- [ ] Comments explain WHY, not WHAT
- [ ] Scaled for 10x current volume, not 100x theoretical
- [ ] Tests teach the business rule, not just assert non-null
- [ ] All assets are idempotent
- [ ] Every asset emits observability metadata

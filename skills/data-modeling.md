# Skill: Data Modeling for Analytics

> *Applied by: Data Architect (02), Analytics Engineer (06)*

---

## The core principle

**A data model is not a technical artifact — it is a shared language between engineers and the business. A model that is technically correct but that analysts can't understand or trust has failed its purpose.**

Good data modeling makes the right answer easy to get and the wrong answer hard to get by accident.

> "A model is done when an analyst can answer a business question correctly the first time, without asking the engineer for help."

---

## The medallion layers and what each one is for

```
Bronze (Raw)          Silver (Cleaned)         Gold (Serving)
────────────          ────────────────         ──────────────
Exact copy of         Cleaned, typed,          Business-ready
source data           deduplicated,            models: facts,
                      anonymized               dimensions, metrics

Never modify          Engineers use this       Analysts use this
Never delete          for debugging            for decisions

Answers:              Answers:                 Answers:
"What did the         "What is the             "What happened
source send?"         canonical record?"       in the business?"
```

**The immutability rule:**
- Bronze is append-only. A record in Bronze is proof of what the source sent.
- Silver is the canonical truth. One row per entity per grain.
- Gold is derived from Silver. If Silver is wrong, Gold re-derives correctly after a fix.

---

## Dimensional modeling — the foundation

### Grain first, always

Before writing a single line of SQL, define the grain of the model in the description:

```yaml
# schema.yml
- name: fct_orders
  description: |
    **Grain: one row per order_id.**
    Each row represents a single order placed by a customer.
    Cancelled orders are included (use is_completed to filter).
    Does NOT include order line items (see fct_order_items for line-level grain).
```

A model without a documented grain is a model that will be misused.

### Fact tables — what happened

Facts contain measures (numbers you aggregate) and foreign keys to dimensions (who, what, where, when).

```sql
-- ✅ Good fact table design
SELECT
    -- Surrogate key (always)
    {{ dbt_utils.generate_surrogate_key(['order_id']) }} AS order_sk,

    -- Natural key (keep for debugging and dedup)
    order_id,

    -- Foreign keys to dimensions
    customer_sk,
    seller_sk,
    DATE_TRUNC(order_date, MONTH) AS order_month_sk,  -- grain of dim_date if exists

    -- Degenerate dimensions (attributes with no separate dimension)
    order_status,
    payment_method,

    -- Measures — what you aggregate
    order_amount_brl,
    discount_amount_brl,
    net_revenue_brl,           -- pre-calculated, not derived at query time

    -- Flags for common filters (avoids repeated CASE WHEN in every query)
    is_completed,
    is_cancelled,
    is_first_order_of_customer,

    -- Metadata
    order_date,
    order_week,
    order_month,
    _loaded_at
FROM ...
```

**What does NOT go in a fact table:**
- Attributes that describe the customer (those live in `dim_customers`)
- Slowly changing attributes (SCD — use dim with effective dates)
- Raw text fields that need to be cleaned (those should be cleaned in Silver)

### Dimension tables — who/what/where

Dimensions describe the entities that participate in facts. They are wide (many columns, few rows relative to facts).

```sql
-- ✅ Good dimension table design
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id']) }} AS customer_sk,

    -- Natural key
    customer_id,

    -- Descriptive attributes (no measures here)
    customer_name,          -- cleaned, title-cased
    customer_segment,       -- derived: 'enterprise' | 'mid-market' | 'smb'
    customer_city,
    customer_state,
    customer_country,

    -- Derived lifecycle attributes
    first_order_date,
    last_order_date,
    lifetime_order_count,
    lifetime_revenue_brl,
    days_since_last_order,
    customer_lifecycle_status,  -- 'active' | 'at_risk' | 'churned'

    -- No PII in Gold
    -- customer_email → removed, was anonymized in Silver
    -- customer_cpf   → removed entirely

    _loaded_at
FROM ...
```

---

## Slowly Changing Dimensions (SCDs)

When a dimension attribute changes over time and history matters:

| Type | When to use | Example | Complexity |
|------|-------------|---------|------------|
| **SCD Type 1** | History doesn't matter | Customer phone number | Low — just overwrite |
| **SCD Type 2** | Full history needed | Customer segment (was SMB, became enterprise) | Medium — add effective dates |
| **SCD Type 3** | Only previous value matters | Sales region reassignment | Low — add "previous_value" column |

```sql
-- SCD Type 2 — snapshot pattern in dbt
-- Use dbt_utils.snapshot or dbt snapshots

-- schema.yml for a Type 2 dimension
- name: dim_customers_scd
  description: |
    **SCD Type 2.** One row per customer per effective period.
    Use is_current = true to get the current state.
    Use effective_from and effective_to to query historical state.
  columns:
    - name: is_current
      description: "True for the customer's current attributes."
    - name: effective_from
      description: "Date this version became active."
    - name: effective_to
      description: "Date this version was superseded. NULL if current."
```

**Default: use SCD Type 1 unless there is a specific business reason for history.** SCD Type 2 adds significant query complexity and maintenance burden.

---

## Naming conventions

Consistent naming removes the need to ask "what does this column mean?"

### Model names
```
stg_[source]__[entity]          staging/stg_erp__orders.sql
int_[entity]_[transformation]   intermediate/int_orders_with_seller_info.sql
fct_[process]                   marts/fct_orders.sql
dim_[entity]                    marts/dim_customers.sql
```

### Column names
| Pattern | Meaning | Examples |
|---------|---------|---------|
| `_id` suffix | Natural key from source | `order_id`, `customer_id` |
| `_sk` suffix | Surrogate key | `order_sk`, `customer_sk` |
| `_at` suffix | Timestamp | `created_at`, `updated_at`, `_loaded_at` |
| `_date` suffix | Date only | `order_date`, `effective_date` |
| `_count` suffix | Integer count | `order_count`, `item_count` |
| `_brl` / `_usd` suffix | Amount with currency | `revenue_brl`, `cost_usd` |
| `is_` prefix | Boolean flag | `is_completed`, `is_first_order` |
| `has_` prefix | Boolean possession | `has_discount`, `has_refund` |
| `n_` prefix | Count (alternative) | `n_orders`, `n_customers` |

**Never use ambiguous names:**
```sql
-- ❌ Ambiguous
revenue, amount, value, total, status, type, flag, date

-- ✅ Specific
net_revenue_brl, order_amount_brl, order_status, payment_type, is_completed, order_date
```

---

## Metrics layer — one definition, many consumers

The most common trust problem: the same metric calculated differently in two places.

```sql
-- ❌ Anti-pattern: metric defined inline in every mart
-- fct_orders:
net_revenue_brl = order_amount_brl - COALESCE(discount_amount_brl, 0)

-- fct_orders_monthly:
monthly_revenue = SUM(order_amount - discount)  -- slightly different!

-- ✅ Pattern: define metric once in intermediate, reference everywhere
-- intermediate/int_orders_enriched.sql
net_revenue_brl = order_amount_brl - COALESCE(discount_amount_brl, 0)

-- fct_orders.sql
SELECT net_revenue_brl FROM {{ ref('int_orders_enriched') }}

-- fct_orders_monthly.sql
SELECT SUM(net_revenue_brl) FROM {{ ref('int_orders_enriched') }}
```

If two people can get different numbers for "total revenue" using different paths in the Gold layer, you have a metric divergence problem. It will be discovered in a board meeting.

---

## Open Table Formats — when and how to apply modeling

When using Delta Lake or Apache Iceberg as the storage layer (instead of pure BigQuery/Snowflake DW), modeling principles remain the same but the implementation differs.

See `skills/modern-data-stack.md` for table format specifics. Modeling implications:

| Decision | Delta Lake | Iceberg | Standard DW (BQ/Snowflake) |
|----------|-----------|---------|---------------------------|
| SCD Type 2 | MERGE + versioning | Time travel queries | Snapshot pattern |
| Incremental | MERGE by natural key | MERGE by natural key | `is_incremental()` in dbt |
| Schema evolution | Automatic (Delta) | Schema evolution API | `ALTER TABLE` or full refresh |
| Historical queries | `VERSION AS OF` | `AS OF TIMESTAMP` | SCD Type 2 only |

---

## Anti-patterns to avoid

| Anti-pattern | Why it's bad | Fix |
|-------------|-------------|-----|
| Grain not documented | Every analyst guesses — some guess wrong | Document grain as first line of model description |
| Measures in dimension tables | Dimensions get stale, measures become wrong | Move measures to facts |
| Join-to-fact in the mart | Cartesian product risk, unexpected row multiplication | Always test for fanout: `COUNT(*) vs COUNT(DISTINCT key)` |
| Everything in one giant mart | God tables are slow and confusing | One mart per business process |
| No surrogate keys | Natural key changes break downstream | Always add surrogate keys in Gold |
| Metrics re-derived at query time | Different analysts get different results | Pre-calculate in intermediate layer |
| No `is_current` on SCDs | Time travel queries become complex | Always add `is_current`, `effective_from`, `effective_to` |

---

## Quick reference: modeling checklist

Before releasing any new Gold model:
- [ ] Grain is documented in the model description
- [ ] Natural key and surrogate key both present
- [ ] Measures pre-calculated (not left to query-time derivation)
- [ ] Boolean flags for common filter patterns
- [ ] No PII in any Gold model
- [ ] Column names follow naming conventions
- [ ] Referential integrity tests exist (FK → dimension)
- [ ] Business logic tests exist (net_revenue ≥ 0, etc.)
- [ ] Model description answers: "what is a row?" without ambiguity
- [ ] If SCD: type documented, `is_current` column present

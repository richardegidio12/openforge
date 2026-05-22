# MCP: Data Warehouse & Query Engines

## BigQuery

**Package:** `mcp-server-bigquery` (community)

**What the Agent can do:**
- Run diagnostic queries directly (freshness, volume, reconciliation)
- Inspect table schemas and metadata
- Check dbt test results via Information Schema
- Analyze query costs before running expensive operations
- Debug data quality issues by querying Silver and Gold directly

**Usage in OpenForge sessions:**

```
# Freshness check during incident
User: "fct_orders looks stale"

Agent (runs query):
SELECT MAX(order_date) as last_date,
       CURRENT_DATE - 1 as expected,
       MAX(order_date) = CURRENT_DATE - 1 as is_fresh
FROM gold.fct_orders

Result: last_date=2024-04-05, expected=2024-04-06, is_fresh=FALSE
"Confirmed: fct_orders was not updated today. Latest data is from yesterday.
Checking the pipeline..."

# Data quality investigation
User: "revenue numbers look wrong for April"

Agent (runs multiple queries):
→ Volume check: 8,431 records for April (normal range: 6k-10k ✅)
→ Status breakdown: 89% completed, 8% cancelled, 3% pending (normal ✅)
→ Reconciliation vs Silver: 0.8% divergence (above 0.5% tolerance ❌)
"Found the divergence. 342 orders in Silver with negative net_revenue —
likely discount greater than order amount. See..."
```

**Setup:**
```json
"bigquery": {
  "command": "npx",
  "args": ["-y", "mcp-server-bigquery"],
  "env": {
    "GOOGLE_APPLICATION_CREDENTIALS": "$GOOGLE_APPLICATION_CREDENTIALS",
    "BIGQUERY_PROJECT_ID": "YOUR_GCP_PROJECT_ID"
  }
}
```

**SA permissions needed:** `bigquery.dataViewer` + `bigquery.jobUser` (read-only is sufficient for diagnostics)

---

## PostgreSQL

**Package:** `@modelcontextprotocol/server-postgres` (official)

**What the Agent can do:**
- Query source databases directly for reconciliation
- Inspect ERP/operational DB schemas when designing ingestion
- Check if the source data matches what was ingested
- Debug ingestion issues by comparing source vs Bronze

**Usage in OpenForge sessions:**

```
# Reconciliation during security/contract review
User: "are you sure the SSN/CPF is no longer in Silver?"

Agent:
→ Queries Silver (BigQuery): confirms customer_cpf column not present ✅
→ Queries ERP source (PostgreSQL): shows customer_cpf still in source ✅
"Confirmed: customer_cpf is in the ERP (expected) but was correctly removed
from Silver. The anonymization pipeline is working."

# Ingestion design
User: "How should we do incremental ingestion for the orders table?"

Agent:
→ Inspects ERP schema: SHOW COLUMNS FROM orders
→ Finds: updated_at TIMESTAMP NOT NULL, INDEX(updated_at)
"The table has updated_at indexed. We can safely use watermark on updated_at.
Volume: 1.2M records, ~2k updates/day."
```

**Setup:**
```json
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres"],
  "env": {
    "POSTGRES_CONNECTION_STRING": "postgresql://readonly_user:$POSTGRES_PASSWORD@host:5432/erp_db"
  }
}
```

**Use a read-only database user.** Never connect with write privileges.

---

## Trino

**Package:** `mcp-server-trino` (community)

**What the Agent can do:**
- Run federated queries across Iceberg, Hive, Delta tables
- Inspect Iceberg table metadata (snapshots, partitions, schema history)
- Query multiple catalogs in one statement for reconciliation
- Check table statistics and partition pruning effectiveness

**Usage in OpenForge sessions:**

```
# Multi-catalog reconciliation
User: "do the Hive and Iceberg counts match?"

Agent:
→ SELECT
    hive.legacy.orders AS hive_count,
    iceberg.silver.orders AS iceberg_count,
    ABS(hive_count - iceberg_count) AS delta
  FROM (
    SELECT COUNT(*) FROM hive.legacy.orders WHERE dt = '2024-04-06'
  ) h,
  (
    SELECT COUNT(*) FROM iceberg.silver.orders WHERE order_date = DATE '2024-04-06'
  ) i

Result: hive=45,231, iceberg=45,229, delta=2
"Difference of 2 records. Likely duplicates handled in Silver.
Investigating..."

# Iceberg time travel for debugging
User: "did yesterday's data change after the backfill?"

Agent:
→ SELECT COUNT(*) FROM iceberg.silver.orders
  FOR TIMESTAMP AS OF TIMESTAMP '2024-04-06 06:00:00'
  WHERE order_date = DATE '2024-04-05'
→ SELECT COUNT(*) FROM iceberg.silver.orders
  WHERE order_date = DATE '2024-04-05'

"Before backfill: 44,891 records.
After backfill: 45,229 records.
The backfill added 338 records that were missing."
```

**Setup:**
```json
"trino": {
  "command": "npx",
  "args": ["-y", "mcp-server-trino"],
  "env": {
    "TRINO_HOST": "YOUR_TRINO_HOST",
    "TRINO_PORT": "8080",
    "TRINO_USER": "openforge_agent",
    "TRINO_PASSWORD": "$TRINO_PASSWORD",
    "TRINO_CATALOG": "iceberg"
  }
}
```

---

## Apache Hive

**Package:** `mcp-server-hive` (community)

**What the Agent can do:**
- Query Hive tables for legacy data reconciliation
- Inspect Hive Metastore schemas and partitions
- Assess migration readiness (Hive → Iceberg)
- Check partition statistics

**Usage in OpenForge sessions:**

```
# Migration assessment
User: "I want to migrate this Hive table to Iceberg — what does it look like?"

Agent:
→ SHOW PARTITIONS hive_legacy.orders LIMIT 10
→ DESCRIBE FORMATTED hive_legacy.orders
→ SELECT COUNT(*) FROM hive_legacy.orders

"The table has 847 date partitions, ORC format, 2.3TB total.
~45M records. No schema evolution issues detected.
Recommended migration strategy: CTAS to Iceberg with partition
by DAY(order_date)..."
```

**Setup:**
```json
"hive": {
  "command": "npx",
  "args": ["-y", "mcp-server-hive"],
  "env": {
    "HIVE_HOST": "YOUR_HIVE_METASTORE_HOST",
    "HIVE_PORT": "10000",
    "HIVE_DATABASE": "default"
  }
}
```

# MCP: Observability Stack

## Grafana

**Package:** `@modelcontextprotocol/server-grafana` (official)

**What the Agent can do:**
- Query dashboards and panels for current values
- Evaluate alert rules status
- Search annotations (incident markers, deployments)
- List and read dashboards by name
- Execute Grafana queries directly

**Usage in OpenForge sessions:**

```
# Check pipeline health dashboard
User: "how are the pipelines right now?"

Agent:
→ Reads "Data Platform Health" dashboard
→ Gets current values for all panels

"Current status (09:47):
Pipeline health: ✅ All jobs running
Last successful runs:
  bronze_orders: 03:12 ✅  (SLO: before 05:00)
  silver_orders: 04:31 ✅
  fct_orders: 05:47 ✅
Volume anomaly: ✅ No alerts
Active alerts: 0 🟢"

# Incident investigation
User: "when did yesterday's problem start?"

Agent:
→ Queries "pipeline_run_duration_seconds" from 01:00 to 04:00
→ Reads annotations for that period

"Grafana shows:
- 01:30: bronze_orders started (normal)
- 02:00: ERP latency rose to 28s (annotation: ERP maintenance)
- 02:17: job failed (annotation: alert fired)
- 02:37: retries exhausted
The problem started when the ERP maintenance window began at 02:00."
```

**Setup:**
```json
"grafana": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-grafana"],
  "env": {
    "GRAFANA_URL": "http://YOUR_GRAFANA_HOST:3000",
    "GRAFANA_API_KEY": "$GRAFANA_API_KEY"
  }
}
```

---

## Prometheus

**Package:** `mcp-server-prometheus` (community)

**What the Agent can do:**
- Execute PromQL queries directly
- Check current metric values and time series
- Evaluate alert rule status (firing/pending/inactive)
- Query metric metadata and labels

**Usage in OpenForge sessions:**

```
# Volume anomaly check
User: "data volume seems low today"

Agent:
→ Runs PromQL:
  pipeline_records_processed_total{job="bronze_orders",date="2024-04-06"}
  vs
  avg_over_time(pipeline_records_processed_total{job="bronze_orders"}[30d])

Result: Today=41,293, 30d avg=44,821, ratio=0.92

"Volume 8% below 30-day average. Within tolerance (alert if < 50%).
May be normal variation. If it persists tomorrow, investigate the source."

# Check active alerts
Agent:
→ GET /api/v1/alerts
→ Filters: state=firing

"2 active alerts:
🟡 ERPResponseTimeHigh: ERP latency > 20s (firing for 3min)
🟢 No critical alerts"

# SLO compliance
Agent:
→ Queries:
  rate(pipeline_run_success_total[30d]) /
  rate(pipeline_run_total[30d]) * 100

"Pipeline availability in the last 30 days: 99.3%
SLO defined: 99%. ✅ Within target."
```

**Setup:**
```json
"prometheus": {
  "command": "npx",
  "args": ["-y", "mcp-server-prometheus"],
  "env": {
    "PROMETHEUS_URL": "http://YOUR_PROMETHEUS_HOST:9090"
  }
}
```

**Note for Thanos:** Thanos Querier exposes a Prometheus-compatible API. Use the same MCP pointing to the Thanos Querier URL instead of Prometheus. This gives you long-term metric history across all clusters.

```json
"thanos": {
  "command": "npx",
  "args": ["-y", "mcp-server-prometheus"],
  "env": {
    "PROMETHEUS_URL": "http://YOUR_THANOS_QUERIER:9090"
  }
}
```

---

## Elasticsearch (ELK Stack)

**Package:** `mcp-server-elasticsearch` (community)

**What the Agent can do:**
- Search pipeline logs by time range, job name, error type
- Aggregate error patterns across pipeline runs
- Find specific batch_id or order_id in logs
- Count error rates and anomaly detection
- Trace a specific record through the pipeline via batch_id

**Usage in OpenForge sessions:**

```
# Find error in logs
User: "I want to understand what happened in yesterday's batch"

Agent:
→ Searches index: pipeline-logs-2024.04.06
  Query: {job_name: "bronze_orders", level: "ERROR", batch_id: "20240406-0130"}

"Found 3 errors in batch 20240406-0130:
02:17:43 ERROR ConnectionRefused: could not connect to erp-host:5432
02:22:43 ERROR ConnectionRefused: retry 2/3 — backing off 5min
02:27:43 ERROR ConnectionRefused: retry 3/3 — job failed
recovery_hint: 'Check ERP connection. Runbook: docs/runbooks/bronze-orders.md'"

# Trace a specific order through the pipeline
User: "did order ORD-12345 make it to Gold?"

Agent:
→ Searches for order_id: "ORD-12345" across bronze, silver, gold logs
→ Builds trace:
  02:17 bronze: ingested ✅ (batch 20240406-0130)
  04:31 silver: transformed ✅ (dedup: kept, net_revenue: $89.90)
  05:47 gold: materialized ✅ (fct_orders, is_completed=true)
"ORD-12345 made it to Gold correctly. Net revenue: $89.90. Status: completed."

# Error pattern analysis
Agent:
→ Aggregates: {terms: {field: "error_type"}, time_range: "last_30_days"}

"Top errors in the last 30 days:
1. ConnectionRefused (ERP): 12 occurrences — 8 between 01:00-04:00
2. SchemaValidationError (silver): 3 occurrences — new field in ERP on 04/03
3. QuotaExceeded (BigQuery): 1 occurrence — analyst ad-hoc query"
```

**Setup:**
```json
"elasticsearch": {
  "command": "npx",
  "args": ["-y", "mcp-server-elasticsearch"],
  "env": {
    "ELASTICSEARCH_URL": "http://YOUR_ES_HOST:9200",
    "ELASTICSEARCH_API_KEY": "$ELASTICSEARCH_API_KEY"
  }
}
```

**Index naming convention (recommended):**
```
pipeline-logs-YYYY.MM.DD     ← structured pipeline logs
access-logs-YYYY.MM.DD       ← BigQuery/data access logs
audit-logs-YYYY.MM.DD        ← security and access control events
```

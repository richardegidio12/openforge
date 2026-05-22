# MCP: Orchestration

## Dagster

**Package:** `mcp-server-dagster` (community)

**What the Agent can do:**
- Check run history and status for any asset or job
- Read full run logs for failed jobs
- Trigger asset materializations and backfills
- Inspect asset metadata (last materialized, freshness)
- View the asset graph and upstream dependencies

**Usage in OpenForge sessions:**

```
# Incident: pipeline failed
User: "the orders job failed last night"

Agent:
→ Gets last 5 runs of bronze_orders_job
→ Reads logs for the failed run at 02:17
Result: "ConnectionRefused to erp-host:5432 at 02:17. 3 retries
         exhausted by 02:37. Error: SSL SYSCALL error: EOF detected"

"Connection failure to ERP PostgreSQL at 02:17.
Likely an unannounced maintenance window.
Should I trigger the backfill now?"

# Trigger backfill
User: "yes, run it"

Agent:
→ dagster asset backfill --select bronze_orders --partition 2024-04-06
→ Monitors run until completion
"Backfill running. 847,231 records processed. Run ID: abc-123.
Status: SUCCESS in 12 minutes."

# Check asset freshness
User: "is everything up to date for today?"

Agent:
→ Gets materialization metadata for: bronze_orders, silver_orders, fct_orders
"bronze_orders: updated at 03:12 ✅
 silver_orders: updated at 04:31 ✅
 fct_orders: updated at 05:47 ✅
All within SLO (07:00)."
```

**Setup:**
```json
"dagster": {
  "command": "npx",
  "args": ["-y", "mcp-server-dagster"],
  "env": {
    "DAGSTER_GRAPHQL_URL": "http://YOUR_DAGSTER_HOST/graphql",
    "DAGSTER_API_TOKEN": "$DAGSTER_API_TOKEN"
  }
}
```

---

## Apache Airflow

**Package:** `mcp-server-airflow` (community)

**What the Agent can do:**
- Check DAG run history and status
- Read task logs for failed runs
- Trigger DAG runs manually
- Pause/unpause DAGs
- Inspect task dependencies and XCom values

**Usage in OpenForge sessions:**

```
# Check DAG status
User: "is the ingestion DAG running normally?"

Agent:
→ GET /api/v1/dags/orders_ingestion/dagRuns?limit=7
Result: 6 success, 1 failed (2024-04-06 02:17)

"6 successful runs in the last 7 days.
Failure on 2024-04-06 02:17 — same time as the ERP maintenance window.
Failed task: extract_erp_orders (duration: 30s before timeout)"

# Read task logs
Agent:
→ GET /api/v1/dags/orders_ingestion/dagRuns/.../taskInstances/extract_erp_orders/logs/1
"Full log: OperationalError: SSL SYSCALL error at attempt 3/3..."

# Trigger DAG
User: "can you trigger the backfill?"

Agent:
→ POST /api/v1/dags/orders_ingestion/dagRuns
  {"conf": {"execution_date": "2024-04-06", "backfill": true}}
"DAG triggered. Run ID: manual__2024-04-06T09:23:00. Monitoring..."
```

**Setup:**
```json
"airflow": {
  "command": "npx",
  "args": ["-y", "mcp-server-airflow"],
  "env": {
    "AIRFLOW_HOST": "http://YOUR_AIRFLOW_HOST:8080",
    "AIRFLOW_USERNAME": "openforge_agent",
    "AIRFLOW_PASSWORD": "$AIRFLOW_PASSWORD"
  }
}
```

---

## Apache Flink

**Package:** `mcp-server-flink` (community)

**What the Agent can do:**
- List running Flink jobs and their status
- Check job metrics (throughput, latency, backpressure)
- Read job exceptions and restart history
- Inspect checkpoint status and lag
- Cancel and restart jobs

**Usage in OpenForge sessions:**

```
# Check streaming pipeline health
User: "is the event streaming job falling behind?"

Agent:
→ GET /jobs/overview
→ GET /jobs/{jobId}/metrics?get=numRecordsInPerSecond,numRecordsOutPerSecond,
                                  currentInputWatermark,latestCheckpointDuration

Result:
- Records in/out: 12,400/s → 11,800/s (small drop, normal)
- Input watermark: 2024-04-06T09:15:23 (current time: 09:15:51 — 28s lag ✅)
- Last checkpoint: 45s ago, duration 2.1s ✅
- Backpressure: none ✅

"Job healthy. 28-second lag is within expected range (SLO: < 60s).
No backpressure detected."

# Diagnose a failing job
User: "the sessions job is crashing"

Agent:
→ GET /jobs/{jobId}/exceptions
"Exception: OutOfMemoryError: Java heap space
Task: SessionWindowAssigner (parallelism 4)
Occurrences: 3 times in the last 2h

Likely cause: user with an abnormally long session accumulating state
in RocksDB. Configure session.timeout.ms or increase TaskManager memory."
```

**Setup:**
```json
"flink": {
  "command": "npx",
  "args": ["-y", "mcp-server-flink"],
  "env": {
    "FLINK_JOBMANAGER_URL": "http://YOUR_FLINK_JOBMANAGER:8081"
  }
}
```

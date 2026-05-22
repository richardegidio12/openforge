# Skill: Observability for Data Platforms

> *Applied by: Data Architect (02), Data Engineer (05), Analytics Engineer (06)*

---

## The core principle

**Observability is not monitoring. Monitoring tells you when something is wrong. Observability tells you why.**

A data platform without observability is a black box. You discover problems when stakeholders complain about wrong numbers, not when the system tells you. This skill makes failures visible, diagnosable, and recoverable — before someone opens a support ticket.

> "If you can't answer 'what happened between 01:00 and 03:00 last Tuesday?' in under 5 minutes, your pipeline is not observable."

---

## The three pillars for data platforms

| Pillar | What it answers | Tools |
|--------|----------------|-------|
| **Metrics** | Is the system healthy right now? | Prometheus, Grafana, CloudWatch, Dagster sensors |
| **Logs** | What exactly happened and when? | ELK Stack (Elasticsearch + Logstash + Kibana), Cloud Logging, Loki |
| **Traces** | Where did this specific record go wrong? | OpenTelemetry, dbt lineage, Dagster asset lineage |

You need all three. Metrics without logs can't tell you why. Logs without metrics can't alert you proactively. Neither without traces can't follow a specific record through the pipeline.

---

## Metrics — what to measure

### Pipeline health metrics (every orchestrated job)
```
pipeline_run_duration_seconds{job, env, status}
pipeline_run_count_total{job, env, status}          # completed / failed / skipped
pipeline_records_processed_total{job, source, layer}
pipeline_records_failed_total{job, source, error_type}
pipeline_last_success_timestamp{job, env}            # the most important one
```

**Alert on:**
- `pipeline_last_success_timestamp` older than expected schedule + buffer (e.g., daily job: alert if > 26h ago)
- `pipeline_records_failed_total` > 0 for PII-related jobs (zero tolerance)
- `pipeline_run_duration_seconds` > 2x the historical median (anomaly detection)

### Data freshness metrics (every Gold table consumed by stakeholders)
```sql
-- Check at 07:00 every day
SELECT
  MAX(order_date) AS last_data_date,
  CURRENT_DATE - 1 AS expected_date,
  MAX(order_date) = CURRENT_DATE - 1 AS is_fresh
FROM gold.fct_orders
```

**Alert if:** `is_fresh = false` → Slack alert before stakeholders arrive at 09:00.

### Data volume metrics (anomaly detection)
```sql
-- Volume should be within historical range
SELECT
  COUNT(*) AS record_count,
  AVG(COUNT(*)) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) AS avg_30d,
  COUNT(*) / AVG(COUNT(*)) OVER (ORDER BY order_date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) AS volume_ratio
FROM gold.fct_orders
GROUP BY order_date
```

**Alert if:** `volume_ratio < 0.5` (sudden drop) or `volume_ratio > 3.0` (unexpected spike).

---

## Logs — what to log and how

### Log levels — when to use each
| Level | When | Example |
|-------|------|---------|
| `ERROR` | Job failed, data corrupted, contract violated | Connection refused, schema mismatch |
| `WARNING` | Recoverable issue, degraded behavior | Retry attempt, soft dedup, join miss |
| `INFO` | Normal operation milestones | Job started, batch_id, record count |
| `DEBUG` | Detailed trace for development | Row-level processing, watermark values |

**Production:** ERROR + WARNING + INFO only. DEBUG off by default, enable per-job when diagnosing.

### What every pipeline log entry must contain
```python
import structlog

log = structlog.get_logger()

# Every log entry must have these fields
log.info(
    "batch_ingested",
    job_name="bronze_orders",
    batch_id=batch_id,
    source="erp_tiny",
    record_count=len(records),
    watermark_used=str(watermark),
    duration_seconds=elapsed,
    env="prod",
)

# Errors must have recovery context
log.error(
    "ingestion_failed",
    job_name="bronze_orders",
    batch_id=batch_id,
    error_type=type(e).__name__,
    error_message=str(e),
    retry_attempt=attempt,
    watermark_used=str(watermark),
    # What the on-call engineer should check
    recovery_hint="Check ERP connection. Last successful run: {last_success}. Runbook: docs/runbooks/bronze-orders.md",
)
```

### What NEVER goes in logs
```python
# ❌ PII in logs — even in dev
log.info("processing customer", email=customer_email, cpf=customer_cpf)

# ✅ Log the ID, never the PII value
log.info("processing customer", customer_id=customer_id, has_email=bool(customer_email))

# ❌ Credentials, tokens, secrets
log.debug("connecting", conn_string=connection_string)

# ✅ Log the intent, not the credential
log.debug("connecting", source="erp_tiny", host=host, port=port)
```

### Log retention policy
| Environment | Level | Retention |
|-------------|-------|-----------|
| Production | ERROR, WARNING | 90 days minimum |
| Production | INFO | 30 days |
| Production | DEBUG | Never in prod |
| Development | All | 7 days |

---

## SLOs — Service Level Objectives for data

Define SLOs before build, not after. These live in the data contract.

| SLO | Example | How to measure |
|-----|---------|----------------|
| **Freshness** | Gold tables updated by 07:00 | `MAX(order_date) = CURRENT_DATE - 1` checked at 07:00 |
| **Completeness** | ≥ 99.5% of ERP orders ingested daily | Record count in Bronze vs ERP source count |
| **Accuracy** | Net revenue divergence from ERP < 0.5% | Reconciliation query in dbt test |
| **Availability** | Pipeline success rate ≥ 99% per month | `successful_runs / total_runs` in Dagster/Airflow |

SLO breaches trigger alerts. SLO trends (gradual degradation) trigger architecture reviews.

---

## Alerting — the right threshold, the right channel

### Alert fatigue is as dangerous as no alerts
An alert that fires every day becomes background noise. Every alert must be:
1. **Actionable** — someone must be able to do something about it
2. **Urgent** — fires before stakeholders notice
3. **Specific** — tells you what to check, not just "something failed"

```yaml
# Good alert — actionable and specific
alert: GoldLayerNotFresh
expr: gold_last_success_timestamp{table="fct_orders"} < (time() - 86400)
for: 30m
annotations:
  summary: "fct_orders Gold not updated — stakeholders arrive at 09:00"
  runbook: "docs/runbooks/fct-orders-freshness.md"
  slack_channel: "#data-incidents"

# Bad alert — noisy, not actionable
alert: PipelineWarning
expr: pipeline_warnings_total > 0
annotations:
  summary: "Pipeline has warnings"
```

### Alert routing
| Severity | Channel | Response time |
|----------|---------|---------------|
| 🔴 Data incorrect/missing in production | #data-incidents + PagerDuty/phone | < 30 min |
| 🟡 Pipeline delayed but not failed | #data-platform | < 2h |
| 🟢 Informational (job completed, backfill done) | #data-platform | No response needed |

---

## Observability in dbt

```yaml
# schema.yml — every model should have freshness and row count checks
models:
  - name: fct_orders
    description: "One row per order. Grain: order_id."
    meta:
      owner: carolina.mendes@company.com
      slo_freshness: "Updated by 07:00 daily"
      slo_completeness: "≥ 99.5% of ERP orders"
    tests:
      - dbt_utils.recency:
          datepart: day
          field: order_date
          interval: 1      # max 1 day old
      - dbt_utils.expression_is_true:
          expression: "COUNT(*) BETWEEN 500 AND 8000"
          # row count SLO from data contract
```

---

## Grafana dashboard structure (standard)

Every data pipeline should have a dashboard with these panels:

```
Row 1: Pipeline Health
  ├── Last successful run (time since)
  ├── Run duration trend (7 days)
  └── Failure count (24h)

Row 2: Data Quality
  ├── Records processed vs expected (volume SLO)
  ├── Failed records count
  └── Freshness status per table (green/red)

Row 3: Infrastructure
  ├── Query bytes processed (cost proxy)
  ├── Memory / CPU of pipeline workers
  └── Source system response time
```

---

## Quick reference: observability checklist per story

Before marking any pipeline story as done:
- [ ] Metrics emitted: job duration, record count, last success timestamp
- [ ] Structured logs with batch_id, source, record_count, watermark
- [ ] No PII in any log entry
- [ ] Alert configured for SLO breach (freshness + volume)
- [ ] Alert tested: failure simulation executed, notification received
- [ ] Runbook exists at `docs/runbooks/[job-name].md`
- [ ] Grafana/dashboard panel exists for this pipeline

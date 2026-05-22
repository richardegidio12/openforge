# Skill: Incident Response for Data Platforms

> *Applied by: Data Engineer (05), Analytics Engineer (06)*

---

## The core principle

**Data incidents are different from application incidents. A web app going down is immediately visible. Data being wrong or stale can go undetected for days — and by then, decisions have been made on bad numbers.**

This skill defines the protocol for detecting, diagnosing, communicating, and recovering from data incidents — fast enough that stakeholders trust the platform, and structured enough that the team learns from every incident.

> "The worst data incident is the one nobody knows about. The second worst is the one everyone knows about and nobody knows how to fix."

---

## Incident classification

| Severity | Definition | Examples | Response SLA |
|----------|-----------|---------|--------------|
| **SEV-1** | Data incorrect or missing in production, impacting business decisions | Wrong revenue in dashboards, PII exposed, pipeline silent for 24h+ | Immediate — < 30 min to first response |
| **SEV-2** | Pipeline delayed but data will be correct; SLO breached | Daily job 4h late, Gold not fresh at SLA time | < 2h to resolution or workaround |
| **SEV-3** | Non-production issue or degraded quality within tolerance | Dev pipeline broken, minor reconciliation gap within contract tolerance | Next business day |
| **SEV-4** | No user impact, internal technical debt | Slow query, noisy alert, test flakiness | Next sprint |

---

## Detection — before stakeholders tell you

Proactive detection is the difference between a team that owns reliability and a team that reacts to complaints.

**Automated checks (must exist for every production pipeline):**
```
07:00 daily → Freshness check: Gold tables updated with D-1 data?
07:15 daily → Volume check: record count within expected range?
Continuous  → Pipeline failure alert: job failed after all retries?
Continuous  → Error rate alert: >1% of records failing transformation?
```

**The escalation path:**
```
Check fails → #data-platform (Slack) → on-call engineer
                                       │
                        If not acknowledged in 15 min
                                       ↓
                        #data-incidents (Slack) + PagerDuty
```

---

## The 5-step response protocol

### Step 1 — Acknowledge (< 5 min)

Post in #data-incidents immediately:
```
🔴 [SEV-1] fct_orders not updated — investigating
On it: @rafael.torres
Started: 08:42
```

Do not start diagnosing before acknowledging. Silence is the worst signal you can send.

### Step 2 — Assess impact (< 15 min)

Before fixing anything, answer:
- What data is affected? (which tables, which date range)
- Who is using it right now? (check dashboard active users, running reports)
- Is the data wrong or just delayed? (wrong = higher severity)
- Is PII involved? (different escalation path — see Security Consultant)

```sql
-- Quick impact assessment queries
-- 1. What's the latest data available?
SELECT MAX(order_date) AS last_date, MAX(_ingested_at) AS last_ingested
FROM gold.fct_orders;

-- 2. Are there records that look wrong?
SELECT order_status, COUNT(*), SUM(net_revenue_brl)
FROM gold.fct_orders
WHERE order_date = CURRENT_DATE - 1
GROUP BY order_status;

-- 3. Did the pipeline run?
-- Check Dagster/Airflow run history for today
```

### Step 3 — Communicate (continuous)

Update the incident thread every 30 minutes, even if you have nothing new:
```
08:42 — Acknowledged. fct_orders last updated 2024-04-05, missing today's data.
09:00 — Root cause found: ERP connection timeout at 02:17. Retries exhausted.
         Working on manual backfill. ETA: 30 min.
09:15 — Backfill running. 847k records to process.
09:28 — Backfill complete. fct_orders current. Validating numbers.
09:35 — ✅ Resolved. Data validated. Total downtime: 5h 35min (SLO breach).
         Runbook updated. Post-mortem scheduled for Friday.
```

**Stakeholder communication:**
```
Subject: [Data Platform] Sales dashboard delayed this morning

The sales data in Metabase was not updated this morning as expected (SLO: 07:00).
Root cause: ERP connectivity issue at 02:17.
Status: Resolved at 09:35. All data is now current and correct.
Impact: Dashboard showed yesterday's data until 09:35.
No data was incorrect — only delayed.

We are reviewing the ERP connection monitoring to prevent recurrence.
```

### Step 4 — Fix and validate

**For delayed data (pipeline didn't run):**
```bash
# Dagster: trigger a backfill for the missed partition
dagster asset backfill --select bronze_orders --partition 2024-04-06

# dbt: re-run affected models
dbt run --select fct_orders+ --full-refresh  # only if incremental state is corrupt
dbt run --select fct_orders+                 # prefer incremental re-run
dbt test --select fct_orders+
```

**For incorrect data:**
1. Stop all downstream consumers from reading the affected table (if possible)
2. Identify the root cause in the source data
3. Fix the source issue or apply a documented correction
4. Reprocess from the point of corruption
5. Run full reconciliation before re-enabling consumers

**Validation before closing:**
```sql
-- Always run these before declaring resolved
-- 1. Freshness
SELECT MAX(order_date) = CURRENT_DATE - 1 AS is_fresh FROM gold.fct_orders;

-- 2. Volume within SLO
SELECT COUNT(*) BETWEEN 500 AND 8000 AS volume_ok
FROM gold.fct_orders WHERE order_date = CURRENT_DATE - 1;

-- 3. Spot reconciliation
SELECT
  (SELECT SUM(net_revenue_brl) FROM gold.fct_orders WHERE order_date = CURRENT_DATE - 1)
  /
  (SELECT SUM(amount - COALESCE(discount,0)) FROM erp_replica.orders
   WHERE order_date = CURRENT_DATE - 1 AND status = 'completed')
  AS reconciliation_ratio
-- Should be between 0.995 and 1.005
```

### Step 5 — Post-mortem (within 48h for SEV-1 and SEV-2)

Post-mortems are blameless. The goal is to understand the system failure, not the human failure.

```markdown
## Post-mortem: fct_orders not updated on 2024-04-06

**Date:** 2024-04-06
**Severity:** SEV-2
**Duration:** 5h 35min (02:17 to 09:35, data delayed — not incorrect)
**Impact:** Sales team could not see today's orders until 09:35

### Timeline
- 02:17 — ERP PostgreSQL connection refused (maintenance window, undocumented by IT)
- 02:17–02:37 — 3 retry attempts with backoff, all failed
- 02:37 — Dagster alert fired to #data-platform
- 08:42 — On-call engineer acknowledged (alert was not seen until morning)
- 09:00 — Root cause identified
- 09:28 — Backfill completed
- 09:35 — Validated and resolved

### Root cause
ERP database had an undocumented maintenance window between 02:00 and 04:00.
Our pipeline runs at 01:30 and retries until 02:37.
The maintenance window started 47 minutes into our retry window.

### Contributing factors
1. IT maintenance windows not shared with data team
2. No alerting escalation to on-call phone — only Slack (not seen overnight)
3. No fallback mechanism for ERP unavailability (just fail vs. use cached metadata)

### Action items
| Action | Owner | Due |
|--------|-------|-----|
| Add PagerDuty escalation for SEV-1/2 after 30min no-ack | Rafael Torres | 2024-04-10 |
| Get IT to share maintenance window calendar | Bruno Costa | 2024-04-12 |
| Adjust pipeline schedule to 03:30 (after maintenance window) | Rafael Torres | 2024-04-08 |
| Add "ERP in maintenance" detection to error handling | Rafael Torres | 2024-04-15 |

### What went well
- Alert fired correctly and immediately
- Backfill was clean and fast
- Stakeholder communication was clear
```

---

## Runbook template (per pipeline)

Every pipeline must have a runbook. Runbooks live at `docs/runbooks/[job-name].md`.

```markdown
# Runbook: bronze_orders

**Owner:** Rafael Torres
**Schedule:** 01:30 BRT daily
**SLO:** Gold data available by 07:00
**Alert channel:** #data-platform → #data-incidents if unacknowledged for 15min

## Common failures

### Connection refused / timeout to ERP
**Symptoms:** `ConnectionRefused` or `OperationalError` in logs
**Check first:** Is IT running maintenance? (ask in #infra-ops)
**Fix:** If maintenance, wait for it to end and trigger manual backfill:
```bash
dagster asset backfill --select bronze_orders --partition <YYYY-MM-DD>
```
**If not maintenance:** Check ERP credentials in Secret Manager haven't expired.

### Duplicate records in Silver
**Symptoms:** dbt test `unique on order_id` fails
**Check first:**
```sql
SELECT order_id, COUNT(*) FROM silver.orders GROUP BY 1 HAVING COUNT(*) > 1 LIMIT 20;
```
**Fix:** ERP duplicate bug. The dedup logic in `silver_orders.py` should handle it.
If not, check the dedup watermark — it may have regressed. See HIST-007 in pipeline-spec.

### GCS write failure
**Symptoms:** `GoogleCloudError` in logs, Bronze file missing
**Check:** Is the file partially written? Check for `_tmp_` prefix in GCS:
```bash
gsutil ls gs://sample-store-data/bronze/orders/ | grep _tmp_
```
**Fix:** Delete the partial file and re-run. Write is atomic only if staging path is used.
```
```

---

## Quick reference: on-call checklist

When you get paged at 2am:

```
1. Don't panic. Check: is the data wrong or just delayed?
   - Wrong = SEV-1, wake people up
   - Delayed = SEV-2, handle alone until business hours

2. Acknowledge in Slack within 5 minutes

3. Run the impact assessment queries (above)

4. Check the runbook for this specific pipeline first

5. If you can't fix in 30 min: escalate + communicate to stakeholders

6. Validate before closing: freshness + volume + spot reconciliation

7. Write the post-mortem. Not optional for SEV-1/SEV-2.
```

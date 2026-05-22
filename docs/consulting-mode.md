# OpenForge as a Data Consultant

Once the Agent has read your project — either during initial setup or through CONSULT MODE — it has enough context to work as a specialized consultant for your specific pipeline.

You don't need to explain the project every time. It already knows what you have.

---

## Real consulting examples

The examples below assume the Agent has already read the `pipeline-sales/` project with:
- Dagster + BigQuery + dbt
- `data-contract-orders.md` in place
- `security-assessment.md` in place
- GCP stack

---

### 🔴 "My pipeline failed last night"

**User:**
> The orders ingestion job failed today at 2:17am. Slack notified me but I don't
> understand the error. What could it be?

**Agent:**

📂 Reading `dagster/assets/bronze_orders.py`, `dagster/resources/erp_resource.py`...

I can see your `bronze_orders` asset uses a watermark on `updated_at` and has retry configured for 3 attempts with 2/5/10 min backoff. If it failed at 2:17am and you received an alert, it means all 3 retries were exhausted — the job started around 1:47am.

The most likely causes for this specific time:

1. **ERP connection timeout** — your `erp_resource.py` has `connect_timeout=30s`. PostgreSQL ERPs often have maintenance windows between 1am–3am. Check ERP logs for table locks at that time.

2. **Corrupted Parquet file from a previous attempt** — if an earlier run aborted mid-write, the file may be incomplete in GCS. Does your code have atomic writes? I see it uses `gcs_client.upload_from_string()` without a staging path.

3. **GCS API quota** — unlikely at your volume, but worth checking.

**Immediate action:** run this command to see the exact error:
```bash
dagster job logs --job-name bronze_orders_job --run-id <last run id>
```

**Preventive action:** add a staging path to the GCS write to guarantee atomicity:
```python
# before the final rename, write to _staging/
staging_path = path.replace("bronze/", "bronze/_staging/")
# ... write ...
gcs_client.copy(staging_path, final_path)
gcs_client.delete(staging_path)
```

⚠️ Noticed while reading: your `erp_resource.py` has the connection string as environment variable `ERP_CONN_STRING`. Is this injected via Secret Manager or via `.env`? The `security-assessment.md` has this as SEC-001 pending.

---

### 📊 "Dashboard numbers don't match the ERP"

**User:**
> The sales team complained that April's total revenue in Metabase is $47k below
> what the ERP shows. This has happened before.

**Agent:**

📂 Reading `dbt/models/marts/fct_orders.sql`, `data-contract-orders.md`, `dbt/models/staging/stg_orders.sql`...

I can see `fct_orders` uses `net_revenue = order_amount - COALESCE(discount_amount, 0)` and the data contract defines a 0.5% tolerance for monthly reconciliation. A $47k difference needs to be investigated in layers.

**Diagnosis in 3 steps:**

**Step 1 — Check if it's a dedup issue:**
```sql
-- Count orders duplicated in Silver that were deduplicated
SELECT order_id, COUNT(*) as cnt
FROM silver.orders
GROUP BY order_id HAVING cnt > 1
```
Your ERP has the duplicates bug (documented in pipeline-spec). If the Silver dedup discarded a valid version, that explains the difference.

**Step 2 — Check orders with excluded status in the filter:**
```sql
-- does fct_orders filter by status?
SELECT order_status, COUNT(*), SUM(net_revenue)
FROM gold.fct_orders
WHERE order_month = '2024-04'
GROUP BY order_status
```
If the ERP counts cancelled orders in gross revenue and dbt filters them out, there's a structural divergence — not a bug, but a different definition of revenue. This needs to be in the data contract.

**Step 3 — Check the April backfill:**
```sql
SELECT DATE(_ingested_at) as ingestion_date, COUNT(*) as orders
FROM silver.orders
WHERE order_month = '2024-04'
GROUP BY 1 ORDER BY 1
```
If any day in April has zero or very few records, there was an ingestion failure without reprocessing.

Which step returned something suspicious? I'll continue the diagnosis from there.

---

### 💰 "Our GCP bill went up 40% this month"

**User:**
> April's bill was $1,850. Last month it was $1,320. We didn't change anything.

**Agent:**

📂 Reading `cost-context.md`, `terraform/main.tf`, `dbt/models/`...

Your budget is $400/month. You're at $1,850 — within the limit, but a 40% jump in one month without declared changes warrants investigation.

Based on your setup, the most likely candidates in order of probability:

**1. BigQuery — bytes processed (most likely)**
You have 47 dbt models. If someone added a Metabase query doing a full table scan on `fct_orders` without using the date partition, costs scale quickly.

Check in BigQuery console:
```sql
SELECT user_email, total_bytes_billed, query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time BETWEEN '2024-04-01' AND '2024-04-30'
ORDER BY total_bytes_billed DESC
LIMIT 20
```

**2. Dagster Cloud — execution time**
If any job started taking longer (perhaps order volume grew), Dagster Serverless charges by execution time. Check job duration history for April vs March.

**3. GCS — egress**
If a new consumer started downloading data from Bronze (analyst, new tool), GCS egress charges apply. Check the bucket access logs.

Which of the three can you check first? I'll help you interpret the result.

---

### 🔒 "Can I give dataset access to an external consultancy?"

**User:**
> A consultancy is doing a 3-week project and needs access to orders data.
> Can I just add their email in BigQuery?

**Agent:**

📂 Reading `security-assessment.md`, `data-contract-orders.md`, `governance-policy.md`...

Not directly — and there are 3 specific points from your project I need to show you first:

**1. The Gold dataset has indirect PII**
Your `fct_orders` has `customer_email_hash` (SHA-256). The hash alone is not PII, but combined with other data the consultancy may have (a customer list, for example), re-identification may be possible. Verify whether the consultancy will cross-reference with external sources.

**2. Your governance-policy requires formal registration of external access**
In the Access Management section of `governance-policy.md`, you defined that third-party access requires approval from the data owner (Carolina Mendes) and registration with an expiration date. This isn't bureaucracy — it's what protects you in a GDPR/LGPD audit.

**3. The correct path for 3 weeks:**

```bash
# 1. Create a temporary SA specific to the consultancy
gcloud iam service-accounts create consultancy-xyz-temp \
  --description="Temporary access consultancy XYZ — expires 2024-05-15"

# 2. Give access ONLY to Gold, read-only
gcloud projects add-iam-policy-binding your-project \
  --member="serviceAccount:consultancy-xyz-temp@..." \
  --role="roles/bigquery.dataViewer" \
  --condition="expression=request.time < timestamp('2024-05-15T00:00:00Z')"

# 3. Document in governance-policy.md with revocation date
```

Should I update `governance-policy.md` with this access documented?

---

### 🏗️ "Does it make sense to add Kafka here?"

**User:**
> My manager read an article and wants to add Kafka for real-time data.
> Does it make sense for our case?

**Agent:**

📂 Reading `architecture-document.md`, `data-product-brief.md`, `cost-context.md`...

Direct answer: **it doesn't make sense for the current use cases**, and I can show you exactly why based on your own architecture.

In `architecture-document.md`, ADR-001 documents that daily batch was chosen because *"all use cases are satisfied with D-1 data available at 07:00"* and *"no use case requires latency under 1 hour"*. Is that ADR still true?

If so, Kafka would introduce:
- **Cost**: Confluent Cloud minimum ~$200/month — that's 50% of your current $400 budget
- **Complexity**: you'd go from 2 simple Dagster assets to producers, consumers, schema registry, dead letter queues
- **2-person team**: Kafka has a steep learning curve and requires continuous operation

**Kafka would make sense if** a real low-latency use case emerged — real-time alerts, live sales dashboards during campaigns, per-transaction fraud detection. Is any of those on the horizon?

If the manager wants "fresher data" without going real-time, a much cheaper alternative is changing the batch from 1x/day to **4x/day** (every 6 hours). At your volume of 2k orders/day, the incremental BigQuery cost would be ~$3/month.

Should I prepare ADR-007 documenting this decision to present to the manager?

---

## The pattern you'll notice

In all examples, the Agent:

1. **Reads the real files before answering** — no generic advice
2. **References artifacts and code by name** — `fct_orders.sql`, `ADR-001`, `cost-context.md`
3. **Responds as the right expert** — the data engineer investigates the pipeline, FinOps analyzes the bill, Security evaluates the access
4. **Offers concrete next actions** — SQL queries, commands, code
5. **Connects the answer to the method** — if the answer reveals a gap in artifacts, offers to update them

The difference from a generic consultant: it doesn't know your ERP has a duplicates bug, your reconciliation tolerance is 0.5%, or your SA has too many `roles/editor` permissions. The OpenForge Agent knows — because it read your project.

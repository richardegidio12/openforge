# Skill: Modern Data Stack & Open Table Formats

> *Applied by: Data Architect (02), Data Engineer (05), Analytics Engineer (06)*

---

## The core principle

**The modern data stack is not a single product — it is a set of interoperable open standards and tools. Choosing well means understanding the trade-offs between managed simplicity and open flexibility.**

The defining shift of the modern era: **open table formats (Iceberg, Delta Lake) decouple storage from compute**. You can change your query engine without changing your data. This is architecturally significant and should inform every storage decision.

> "Don't choose a table format for its features. Choose it for who your query engine is and who you might want it to be in 3 years."

---

## Open Table Formats — when to use which

### Apache Iceberg

**Best for:** Multi-engine environments, long-term interoperability, cloud-neutral architectures.

```
Strengths:
+ Engine-agnostic: Spark, Trino, Flink, Athena, BigQuery Omni, Hive, DuckDB
+ ACID transactions at the table level
+ Schema evolution without rewrites (add/rename/drop columns safely)
+ Time travel (query any snapshot by timestamp or snapshot ID)
+ Partition evolution (change partitioning strategy without rewrites)
+ Hidden partitioning (engine handles partitioning transparently for queries)
+ Open spec (Apache Software Foundation) — no vendor lock-in

Limitations:
- More configuration than Delta Lake
- Catalog required (Hive Metastore, AWS Glue, Nessie, REST catalog)
- Less mature Flink support vs Delta (improving rapidly)

When to choose Iceberg:
→ Multi-engine query (Trino + Spark + Flink on same data)
→ Cloud-neutral or multi-cloud
→ Long-term open-source commitment
→ Need partition evolution without full rewrites
```

### Delta Lake

**Best for:** Spark-centric environments, Databricks ecosystem, teams already invested in Spark.

```
Strengths:
+ First-class Spark integration (Delta is a Databricks project)
+ DeltaTable API for programmatic operations
+ Automatic schema enforcement
+ Change Data Feed (CDC built-in)
+ Liquid Clustering (automatic data layout optimization)
+ Strong community + Databricks support
+ dbt-delta adapter available

Limitations:
- Better on Spark than other engines (Trino support is good but Spark is first-class)
- Databricks ecosystem pull (Delta Sharing, Unity Catalog)
- Less portable than Iceberg for truly heterogeneous stacks

When to choose Delta Lake:
→ Spark is your primary engine
→ Databricks platform in use or under consideration
→ CDC pipelines where Change Data Feed is valuable
→ Team familiar with Databricks ecosystem
```

### Apache Hudi

**Best for:** High-frequency upserts, CDC workloads, teams needing record-level incremental processing.

```
Strengths:
+ Optimized for high-frequency upserts (Uber use case)
+ Record-level incremental queries (very efficient CDC)
+ Timeline-based metadata for auditing

Limitations:
- More complex than Iceberg/Delta for batch use cases
- Smaller community
- Fewer integrations than Iceberg/Delta

When to choose Hudi:
→ High-frequency streaming upserts (millions/hour)
→ Record-level CDC from databases (Debezium → Hudi)
→ Uber/fintech-style microbatch patterns
```

### Decision guide

```
What is your primary query engine?
  └→ Spark/Databricks → Delta Lake (first choice) or Iceberg
  └→ Trino → Iceberg (best Trino support)
  └→ Multiple engines → Iceberg (most interoperable)
  └→ Flink + Spark → Iceberg or Hudi (both have good Flink support)
  └→ DuckDB (local/small team) → Iceberg or Delta (both supported)

Do you need CDC / high-frequency upserts?
  └→ Yes → Hudi or Delta (Change Data Feed)
  └→ No → Iceberg or Delta

Are you cloud-neutral or planning multi-cloud?
  └→ Yes → Iceberg (no vendor affinity)
  └→ No → Delta Lake (if Databricks) or Iceberg (if AWS/GCP native)

Is Databricks in your stack or roadmap?
  └→ Yes → Delta Lake
  └→ No → Iceberg
```

---

## Query Engines

### Trino (formerly PrestoSQL)

**Role:** Distributed SQL query engine. Reads data where it lives — S3, GCS, HDFS, Iceberg, Delta, Hive — without moving it.

```
Best for:
+ Ad-hoc analytics at scale on data lake
+ Federated queries (join S3 + PostgreSQL + Kafka in one query)
+ Replacing Hive for interactive queries (10x+ faster)
+ Multi-catalog queries

Not for:
- ETL transformations (use Spark)
- Streaming (use Flink)
- OLTP (not a transactional engine)

Trino + Iceberg pattern:
CREATE TABLE iceberg.analytics.fct_orders (
  order_id VARCHAR,
  order_date DATE,
  net_revenue_brl DECIMAL(10,2)
)
WITH (
  format = 'PARQUET',
  partitioning = ARRAY['month(order_date)']
);

-- Time travel
SELECT * FROM iceberg.analytics.fct_orders
FOR TIMESTAMP AS OF TIMESTAMP '2024-03-01 00:00:00';
```

### Apache Spark

**Role:** Distributed compute engine for large-scale batch and streaming transformations.

```
Best for:
+ Large-scale batch ETL (TB-scale transformations)
+ ML feature engineering at scale
+ Complex transformations not expressible in SQL
+ Streaming (Spark Structured Streaming)

Spark + Delta Lake pattern (PySpark):
from delta.tables import DeltaTable

# Upsert (MERGE) — idiomatic Delta pattern
delta_table = DeltaTable.forPath(spark, "s3://datalake/silver/orders")

delta_table.alias("target").merge(
    source=new_orders.alias("source"),
    condition="target.order_id = source.order_id"
).whenMatchedUpdateAll(
).whenNotMatchedInsertAll(
).execute()

Spark + Iceberg:
spark.sql("""
  MERGE INTO catalog.silver.orders t
  USING new_orders s ON t.order_id = s.order_id
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *
""")
```

### Apache Flink

**Role:** Stateful stream processing. The primary engine for real-time data pipelines.

```
Best for:
+ Real-time event processing (< 1s latency)
+ Stateful aggregations on streams (session windows, tumbling windows)
+ CDC ingestion and transformation
+ Exactly-once processing guarantees

Not for:
- Batch-first workloads (Spark is simpler)
- Ad-hoc analytics (use Trino)

Flink + Iceberg (streaming sink):
Table sink = Table.builder()
    .tableLoader(tableLoader)
    .overwrite(false)
    .build();

DataStream<RowData> stream = ...;
sink.forRowData(stream).build();

Flink windowing (event time):
stream
  .keyBy(order -> order.getSellerId())
  .window(TumblingEventTimeWindows.of(Time.hours(1)))
  .aggregate(new RevenueAggregator())
  .addSink(icebergSink);
```

---

## Data Catalog & Governance Layer

### Apache Hive Metastore (HMS)

The original table catalog. Still the most common for on-prem and multi-engine setups.

```
Role: Central schema registry — stores table locations, schemas, partitions
Use when: Already in the stack, or when Iceberg/Hive on-prem
Limitation: HMS is becoming a legacy choice for cloud-native stacks
```

### Project Nessie (Git for data)

**Role:** Catalog for Iceberg with Git-like branching semantics.

```
Key concept: Data branches, just like code branches.

nessie.create_branch("feature/new-revenue-model")
# ... make changes to Iceberg tables on this branch ...
nessie.merge_branch("feature/new-revenue-model", into="main")

Use when:
+ Iceberg + need for data versioning / branching
+ dbt + Iceberg (dbt-nessie adapter)
+ Audit-heavy environments
```

### Apache Ranger

**Role:** Centralized security and access control for the Hadoop/Spark ecosystem.

```
What it governs:
+ HDFS, Hive, HBase, Kafka, Trino, Spark — all in one policy
+ Column-level and row-level security
+ Data masking (mask PII columns for non-privileged users)
+ Audit logging for all data access

Use when:
+ On-prem or hybrid Hadoop ecosystem
+ Need centralized policy (not per-service IAM)
+ Column/row-level security across multiple engines
+ LGPD/GDPR audit requirements at the query engine level

Row-level filter example (Ranger policy):
{
  "name": "mask_customer_email_for_analysts",
  "resources": {"table": "silver.orders", "column": "customer_email"},
  "users": ["analyst_group"],
  "dataMaskInfo": {"dataMaskType": "MASK_HASH"}
}
```

---

## Columnar file formats

| Format | Best for | Compression | Schema evolution |
|--------|---------|-------------|-----------------|
| **Parquet** | Analytics (columnar reads), default for Iceberg/Delta | Excellent | Add columns only |
| **ORC** | Hive-native workloads, on-prem Hadoop | Excellent | Add columns only |
| **Avro** | Row-oriented, serialization, Kafka schemas | Good | Full (add/remove/rename) |
| **Delta/Iceberg** | Not a file format — uses Parquet underneath + metadata layer | Same as Parquet | Full (via table format spec) |

**Default recommendation:** Parquet for everything unless you're in a Kafka/streaming pipeline where Avro schema registry is already in use.

---

## Architecture patterns

### Data Lakehouse (most common modern pattern)

```
[Sources] → [Ingestion] → [Bronze — raw Parquet/Iceberg on S3/GCS]
                                    ↓
                          [Silver — Iceberg with MERGE/ACID]
                                    ↓
                          [Gold — Iceberg or DW (Snowflake/BigQuery)]
                                    ↓
                    [Trino / Spark SQL / DuckDB] ← query engines
                                    ↓
                    [BI Tools / APIs / ML Features]
```

### Lambda architecture (batch + streaming)

```
[Sources]
   ├→ [Batch layer: Spark → Bronze → Silver (T+1)]
   └→ [Speed layer: Flink → Real-time views (< 1min)]
              ↓
   [Serving layer: merged view via Trino]
```

**When to use:** Only when you genuinely need both < 1min latency AND historical batch correctness. Lambda is complex — evaluate Kappa (stream-only) first.

### Kappa architecture (stream-only)

```
[Sources] → [Kafka] → [Flink (stateful stream processing)]
                            → [Iceberg sink — compacted batch files]
                            → [Real-time state store (RocksDB)]
                                        ↓
                            [Trino — unified query layer]
```

**When to use:** When streaming is the primary ingestion pattern and you can express all transformations as stream operations.

---

## Stack selection guide for small teams

```
Team size: 1-3 engineers, cloud-native, < 10TB
→ BigQuery or Snowflake (managed DW, no infra ops)
→ dbt Core for transformations
→ Dagster or Prefect for orchestration
→ No open table format needed — managed DW handles it

Team size: 3-8 engineers, cost-sensitive or multi-cloud
→ S3/GCS + Apache Iceberg + Trino
→ Spark for heavy transformations
→ dbt-spark or dbt-trino for modeling
→ Airflow or Dagster for orchestration
→ Nessie or AWS Glue as catalog

Team size: 8+ engineers, Spark-heavy or Databricks
→ Delta Lake on S3/ADLS
→ Databricks or Spark on EKS/GKE
→ dbt-databricks or Delta API for modeling
→ Databricks Workflows or Airflow

Real-time requirements (any team size)
→ Add Apache Flink for stream processing
→ Keep batch layer for historical correctness
→ Iceberg as the unified storage format
```

---

## Kubernetes deployment patterns (EKS / AKS / GKE)

Running Spark or Flink on Kubernetes is increasingly the standard for cloud-native data platforms.

```yaml
# Spark on Kubernetes — SparkApplication (Spark Operator)
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: silver-orders-job
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster
  image: my-registry/spark-jobs:3.4.0
  mainApplicationFile: "s3a://jobs/silver_orders.py"
  sparkVersion: "3.4.0"
  driver:
    cores: 1
    memory: "2g"
    serviceAccount: spark-sa
  executor:
    cores: 2
    instances: 3
    memory: "4g"
  dynamicAllocation:
    enabled: true
    maxExecutors: 10
```

```yaml
# Flink on Kubernetes — FlinkDeployment (Flink Operator)
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: orders-stream-processor
spec:
  image: my-registry/flink-jobs:1.18
  flinkVersion: v1_18
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "2"
    state.backend: rocksdb
    state.checkpoints.dir: s3://checkpoints/orders-processor
  serviceAccount: flink-sa
  jobManager:
    resource: {memory: "2048m", cpu: 1}
  taskManager:
    resource: {memory: "4096m", cpu: 2}
  job:
    jarURI: s3://jars/orders-processor.jar
    parallelism: 4
    upgradeMode: stateless
```

---

## Quick reference: modern stack decision checklist

When the Data Architect defines the stack:
- [ ] Table format chosen with justification (Iceberg / Delta / none — managed DW)
- [ ] Query engine matches table format (Trino + Iceberg, Spark + Delta)
- [ ] Catalog defined (HMS / Glue / Nessie / Databricks Unity)
- [ ] Access control layer defined (Ranger / cloud IAM / Databricks permissions)
- [ ] File format defined (default: Parquet)
- [ ] Streaming requirement confirmed before adding Flink (avoid premature complexity)
- [ ] K8s deployment considered if Spark/Flink (vs managed EMR/Dataproc — cost trade-off)
- [ ] Schema evolution strategy defined (especially for Avro/Kafka schemas)

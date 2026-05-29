# ADR-012 — Connector Architecture

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** Abstracting the execution engine so OpenForge pipelines can target DuckDB locally and cloud warehouses/query engines in production.

---

## Context

Phase 1–3 was DuckDB-only (local-first). Phase 4 needs to support:
- **Trino** — distributed SQL query engine (requested explicitly)
- **BigQuery** — Google Cloud DW
- **Snowflake** — Cloud DW

The abstraction must:
- Not change the pipeline.yaml format significantly
- Not change agent code (agents shouldn't know which engine they're on)
- Make adding new connectors a single-file addition

## Decision

**Abstract base class `BaseConnector`** with 5 operations: `test_connection`, `table_exists`, `get_column_names`, `create_table_from_records`, `execute`.

**Registry pattern** (`connectors/registry.py`): `get_connector(config_dict)` → returns the right concrete connector.

**Pipeline.yaml gains an optional `connector:` section** (absent = DuckDB default):

```yaml
connector:
  type: trino
  host: localhost
  port: 8080
  catalog: hive
  schema: analytics
```

**Connector implementations:**

| File | Status |
|------|--------|
| `duckdb_connector.py` | ✅ Production |
| `trino_connector.py` | ✅ Production |
| `stubs.py` (BigQuery, Snowflake) | 🔲 Stub — raises NotImplementedError |

## Trino connector specifics

**Connection:** via `trino` Python client (`pip install trino`).

**Write strategy for MVP:** DDL inferred from first record + batched INSERT (1000 rows/batch). Suitable for ≤ 1M rows.

**Write strategy for large datasets (Phase 4+):** write to Parquet locally → CREATE TABLE pointing at S3/HDFS location. This requires a storage layer (S3, MinIO, HDFS) which is out of scope for the current MVP.

**Trino-specific extras:** `list_catalogs()`, `list_schemas()`, `list_tables()`, `run_query()` — exposed via `openforge connect trino` command for exploration.

## Alternatives Rejected

| Alternative | Reason rejected |
|-------------|----------------|
| SQLAlchemy as abstraction | Heavy, adds ORM complexity we don't need |
| One class per engine (no base) | Coupling — agents would have `if isinstance` checks everywhere |
| `connector.yaml` separate file | Splitting config across 2 files is worse DX than one `pipeline.yaml` |
| Airflow/dbt connectors | Out of scope — those are orchestration layers, not query engines |

## Consequences

- **Positive:** Adding a new connector = create one file implementing `BaseConnector`
- **Positive:** All existing pipelines continue to work unchanged (DuckDB default)
- **Positive:** `openforge connect trino` lets users explore a Trino cluster before writing a pipeline
- **Tradeoff:** Trino batch INSERT is slow for large datasets — acceptable for Phase 4 MVP, needs Parquet path for production workloads
- **Future:** `openforge connect bigquery` and `openforge connect snowflake` unblock when stubs are implemented

## Quick start (Trino local via Docker)

```bash
docker run -d --name trino -p 8080:8080 trinodb/trino
openforge connect trino --host localhost --catalog tpch --schema sf1
openforge run pipeline_trino.yaml
```

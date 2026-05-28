# ADR-008 — DuckDB as Schema Inference and Warehouse Engine

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** Choosing the query engine for local schema inference and data storage in Phase 1.

---

## Context

The MVP needs to:
1. Infer schema and profile columns from CSV/Parquet files
2. Store ingested data locally for quality checks and queries
3. Provide a migration path to cloud data warehouses (BigQuery, Snowflake, Redshift) in Phase 4

## Decision

**DuckDB** for both schema inference (`DESCRIBE SELECT * FROM 'file.csv'`) and the local warehouse (`.openforge/warehouse.db`).

## Why DuckDB wins here

| Requirement | DuckDB fit |
|-------------|-----------|
| Zero-server local storage | ✅ Single file, no daemon |
| SQL-complete queries | ✅ Full ANSI SQL + window functions |
| Native CSV/Parquet reading | ✅ `SELECT * FROM 'file.csv'` just works |
| Column profiling | ✅ `DESCRIBE`, `SUMMARIZE`, `COUNT DISTINCT` |
| Python integration | ✅ `import duckdb` — no configuration |
| Horizontal scalability | ✅ Multi-threaded, columnar execution |
| Cloud migration story | ✅ Same SQL dialect as BigQuery/Snowflake/Redshift |

## Alternatives Rejected

| Alternative | Reason rejected |
|-------------|----------------|
| pandas | Not a database — no SQL, no persistence, memory-bound |
| SQLite | Row-oriented, no native CSV reading, slow for analytics |
| Polars | Fast DataFrame but no server/persistence layer |
| PostgreSQL | Requires a running server — violates local-first principle |
| MotherDuck | DuckDB-as-cloud — perfect for Phase 4, not Phase 1 |

## Consequences

- **Positive:** Schema inference is a single `DESCRIBE` call — trivial to implement
- **Positive:** Quality checks run as standard SQL — easy to extend
- **Positive:** `.openforge/warehouse.db` is a single portable file
- **Positive:** Same SQL runs locally and in cloud DWs — code reuse in Phase 4
- **Tradeoff:** DuckDB is single-writer; concurrent write scenarios need PostgreSQL (Phase 4)
- **Migration path:** Phase 4 introduces connector abstraction; DuckDB becomes the default adapter, with BigQuery/Snowflake/Redshift as alternatives

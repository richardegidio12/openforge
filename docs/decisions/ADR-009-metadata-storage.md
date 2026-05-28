# ADR-009 — Metadata Storage Format

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** How to persist project metadata (schemas, lineage, quality results, run history) locally.

---

## Context

Every Forge Agent reads and writes project state: table schemas, quality results, ingestion records, and run history. We need a storage format that:

- Requires zero infrastructure (local-first)
- Is human-readable and debuggable
- Is version-controllable
- Has a clear migration path to a real database

## Decision

**JSON flat file at `.openforge/metadata.json`**, validated and typed via Pydantic v2 models.

The `ProjectMetadata` Pydantic model is the schema. The store module (`metadata/store.py`) is the only interface — agents never read the file directly.

## Structure

```
.openforge/
├── metadata.json   ← project state (tables, quality, runs)
└── warehouse.db    ← DuckDB (gitignored)
```

## Alternatives Rejected

| Alternative | Reason rejected |
|-------------|----------------|
| SQLite for metadata | Adds schema migration complexity with no benefit at MVP scale |
| YAML | Less standard for machine-generated data; no native typing |
| Multiple JSON files (one per table) | More files to manage; harder to load atomically |
| In-memory only | State lost between runs — fundamentally wrong for an agent platform |
| PostgreSQL | Requires server — violates local-first principle for Phase 1 |

## Consequences

- **Positive:** `cat .openforge/metadata.json` shows the full project state — trivially debuggable
- **Positive:** JSON is git-diffable — every schema change is visible in `git diff`
- **Positive:** Pydantic models = automatic validation on every read — corrupt state is caught immediately
- **Positive:** `metadata.json` can be committed → teams share project state via git
- **Tradeoff:** No concurrent writes (single-user Phase 1 — acceptable)
- **Tradeoff:** Performance degrades above ~10K tables (not a Phase 1 concern)
- **Migration path:** In Phase 4, `store.py` gets a PostgreSQL backend. Models stay identical. Agents don't change.

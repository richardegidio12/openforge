# PROJECT-CONTEXT — OpenForge Platform

> Runtime session state. Updated at the end of each build session.
> New contributors: read this first — it's your 5-minute onboarding.

---

## Quick State

| Field | Value |
|-------|-------|
| Phase | Method evolution — post-MVP |
| Status | 🟢 Stable — platform built, method significantly expanded this session |
| Last session | 2026-05-28 |
| Next action | Push to origin → review docs → plan next evolution |

---

## Decision Anchors (locked — do not change without ADR)

| Parameter | Value | Locked in |
|-----------|-------|-----------|
| Runtime language | Python 3.11+ | ADR-007 |
| Local warehouse | DuckDB | ADR-008 |
| Schema validation | Pydantic v2 | ADR-007 |
| CLI framework | Typer + Rich | ADR-007 |
| LLM provider | Anthropic (direct SDK) | ADR-011 |
| Config format | YAML + Pydantic | ADR-010 |
| Metadata persistence | JSON flat file (`.openforge/metadata.json`) | ADR-009 |
| Target environment | Local-first, cloud-ready (Phase 4) | Phase plan |
| PII handling | Not in scope for Phase 1 | Phase plan |

---

## Team & Stack

| Role | Who |
|------|-----|
| Founder / PM | Richard Egidio |
| AI pair | Claude (Anthropic) |
| Repo | github.com/richardegidio12/openforge |

---

## Artifacts

| File | Purpose |
|------|---------|
| `openforge/cli.py` | CLI entry point (init, run, status) |
| `openforge/agents/schema.py` | Schema inference via DuckDB DESCRIBE |
| `openforge/agents/ingestion.py` | CSV → DuckDB loader |
| `openforge/agents/quality.py` | Declarative quality checks |
| `openforge/pipeline/runner.py` | Pipeline orchestrator |
| `openforge/llm/client.py` | Anthropic API wrapper |
| `openforge/metadata/models.py` | Pydantic models (source of truth) |
| `openforge/metadata/store.py` | Read/write `.openforge/metadata.json` |
| `pipeline.yaml` | Demo pipeline for sales_data |
| `sample_data/sales.csv` | 50-row demo dataset |
| `pyproject.toml` | Package config + dependencies |
| `docs/decisions/ADR-007..011` | Platform implementation ADRs |

---

## Key Decisions (append-only)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-28 | Option B (MVP spike) over spec-first or monorepo-first | Fastest path to working end-to-end demo |
| 2026-05-28 | OpenForge building OpenForge (dogfooding) | ADRs and PROJECT-CONTEXT.md track every decision made while building the platform |
| 2026-05-28 | DuckDB as inference + warehouse engine | Zero-server, SQL-complete, fast, trivial migration to cloud DWs |
| 2026-05-28 | Anthropic SDK directly (no LangChain) | Full control over prompts/tokens/errors; LangChain adds overhead with no benefit at this scale |
| 2026-05-28 | JSON flat file for metadata v0 | Human-readable, zero deps, clear migration path to PostgreSQL in Phase 4 |
| 2026-05-28 | YAML + Pydantic for pipeline definitions | Git-diffable, validated, familiar to data engineers |

---

## Open Items

- [ ] Logo: Richard hasn't chosen between 3 concepts yet
- [ ] Tests: `tests/test_schema_agent.py`, `tests/test_quality_agent.py`
- [ ] `templates/CONTEXT.md` — review and validate with real project

---

## Session Log (last 5)

| Session | Work done |
|---------|-----------|
| 2026-05-28 (3) | Persona 09 AI/ML Engineer (RAG, evals, agents, AI observability). Thematic grills: /grill-rag, /grill-etl, /grill-agent, /grill-migration. Explicit Ask/Plan/Agent modes. Checkpoint Protocol. Escalation Policy. Parallel Track Protocol. Task Board. /refine command. templates/tasks.md. templates/CONTEXT.md. |
| 2026-05-28 (2) | Per-persona Grill Protocol added to all 8 personas (10 questions + cross-reference each). /grill and /grill-docs slash commands. ADR-013 documenting the decision. |
| 2026-05-28 (1) | Defined 5-phase platform roadmap. MVP spike: pyproject.toml, all agents, pipeline runner, CLI, connectors (DuckDB + Trino), SDK, Web UI, chat, heal, inspect. ADRs 007–012. Phase 5: SDK + Plugin API + Web dashboard. |
| Prior | Published to GitHub, SSH key setup, English translation, slash commands, determinism protocol, SDD discovery, brownfield mode, consulting mode. |

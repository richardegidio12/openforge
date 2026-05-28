# ADR-007 — Python Stack for OpenForge Platform

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** Choosing the implementation language and core libraries for the OpenForge runtime.

---

## Context

OpenForge is evolving from a Markdown-based AI method into an executable platform. We need to choose a language runtime, CLI framework, data validation library, and packaging approach that:

- Has a rich data engineering ecosystem
- Supports rapid prototyping (MVP spike approach)
- Is already familiar to the target audience (data engineers)
- Has first-class LLM/AI library support

## Decision

**Python 3.11+** as the runtime language, with:

| Component | Choice |
|-----------|--------|
| CLI | Typer (type-annotated, auto-help generation) |
| Terminal UI | Rich (tables, progress, colors — zero config) |
| Data validation | Pydantic v2 (fast, Rust core, excellent serialization) |
| Packaging | `pyproject.toml` with `hatchling` build backend |

## Alternatives Rejected

| Alternative | Reason rejected |
|-------------|----------------|
| Go | Excellent for CLIs but poor data/AI library ecosystem |
| TypeScript/Node | Strong ecosystem but weaker data stack integration |
| Rust | Too low-level for rapid MVP iteration |
| Click (instead of Typer) | Typer wraps Click with type annotations — strictly better for our use case |
| argparse | Too verbose, poor developer experience |
| dataclasses (instead of Pydantic) | No validation, no serialization, no JSON schema |

## Consequences

- **Positive:** Every data engineer can read, fork, and contribute to the codebase
- **Positive:** Anthropic SDK, DuckDB, pandas, Polars all available as deps
- **Positive:** `pip install openforge` works on any machine with Python 3.11+
- **Tradeoff:** Python startup time is slower than Go/Rust CLIs (acceptable for data workloads where the bottleneck is IO, not process spawn)
- **Migration path:** Core logic can be wrapped in a Rust extension (via PyO3) later if performance becomes critical

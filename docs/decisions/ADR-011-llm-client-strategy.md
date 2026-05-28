# ADR-011 — LLM Client Strategy

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Richard Egidio, Claude  
**Context:** How OpenForge calls LLMs for AI-powered features (doc generation, prompt → pipeline, self-healing).

---

## Context

OpenForge needs LLM capabilities for:
- Phase 1: Column/table documentation generation
- Phase 2: Natural language → pipeline YAML
- Phase 3: Failure classification and patch suggestion
- Phase 4+: RAG over metadata, SQL generation, conversational interface

We need a client strategy that is simple, controllable, and doesn't add unnecessary abstraction.

## Decision

**Anthropic Python SDK directly** (`anthropic` package), with a thin wrapper in `openforge/llm/client.py`.

No LangChain. No LlamaIndex. No framework.

The wrapper provides:
1. Lazy client initialization (fail fast if `ANTHROPIC_API_KEY` missing)
2. Prompt templates as Python f-strings (readable, no DSL to learn)
3. JSON extraction from responses (defensive parsing)
4. Model name centralized in one constant (`MODEL = "claude-opus-4-5"`)

## Why direct SDK over frameworks

| Concern | Direct SDK | LangChain / LlamaIndex |
|---------|-----------|----------------------|
| Prompt visibility | Full — it's a Python string | Hidden behind chain abstractions |
| Error messages | SDK errors are clear | Framework wraps them, adds noise |
| Token control | Explicit `max_tokens` | Managed by framework (surprise costs) |
| Upgrade path | Update one dep | Update framework + all adapters |
| Lines of code | ~40 lines | ~10 lines + 200 lines of transitive deps doing magic |
| Debug experience | Print the prompt string | Trace through chain callbacks |
| AI generation of prompts | Trivial (it's a string) | Need to know chain DSL |

At MVP scale, the overhead of a framework has no payoff.

## Consequences

- **Positive:** Every prompt is visible and auditable in `llm/client.py`
- **Positive:** Zero magic — anyone can read the code and understand exactly what's sent to the API
- **Positive:** Easy to add retry logic, streaming, or cost tracking without fighting the framework
- **Positive:** OpenForge is vendor-aware but not vendor-locked — swapping Anthropic for OpenAI is a 10-line change in `client.py`
- **Tradeoff:** We write prompt templates manually — acceptable, and better for quality control
- **Future:** If RAG complexity grows in Phase 3, evaluate adding a minimal vector store abstraction (e.g., `chromadb` directly, not via LangChain)

## Model selection

Default: `claude-opus-4-5` (high quality for documentation).  
Future: configurable per feature (fast model for schema inference hints, slow model for architecture analysis).

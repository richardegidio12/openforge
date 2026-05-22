# ADR-001: Persona-based approach over single unified agent

**Date:** 2024-03-01
**Status:** Accepted
**Context:** OpenForge design — fundamental architecture of the method

---

## Context

When designing an AI-driven method for data engineering, the foundational question is: should the AI act as a single general-purpose assistant, or as multiple specialized personas, each with deep expertise in one phase?

The choice determines everything: how users interact with the system, the quality of output per phase, how the method scales, and how contributors extend it.

---

## Decision

OpenForge uses **multiple specialized personas**, each with a distinct identity, scope, behavioral instructions, and output artifact. A single session engages one persona at a time. Personas communicate through artifacts, not directly.

---

## Rationale

**1. Specialization produces better output**
A persona that only thinks about data contracts — asking only the right questions, applying only the relevant principles, producing only the right artifact — produces better output than a general-purpose assistant trying to do everything at once. Deep context in a narrow domain beats shallow context in a wide domain.

**2. Explicit phase boundaries reduce cognitive load on the user**
When the Orchestrator says "now you're talking to the Data Architect", the user knows exactly what to expect, what to provide, and what they'll receive. A single agent that does "everything" is harder to use correctly — the user never knows which mode they're in.

**3. Modular personas are independently maintainable**
A bug in the Data Architect persona doesn't require touching the Pipeline Planner. A new domain (e.g., ML Engineering) can be added as a new persona without changing existing ones. Contributors can improve one persona without understanding the whole system.

**4. Personas match how teams already think about roles**
Data teams already have mental models around "the architect", "the engineer", "the governance person". Mapping personas to these roles makes onboarding faster and the method more intuitive.

---

## Alternatives considered

### Single general-purpose agent
- **Rejected because:** Output quality degrades when one agent must simultaneously be architect, engineer, governance advisor, and security consultant. The agent either becomes generic (no deep expertise) or confused (context pollution between domains).

### Role-switching single agent with system prompts
- **Rejected because:** Functionally equivalent to personas, but without the explicit artifact-mediated boundaries. Artifacts force a clean handoff and a human checkpoint — this is a feature, not a limitation.

### Hierarchical agent tree (manager + worker agents)
- **Considered for v2:** OpenForge v1 uses human-mediated artifact passing. Agent-to-agent communication (via MCP or tool calls) is architecturally possible and may be added in a future version. The persona design is forward-compatible with this.

---

## Consequences

- **Positive:** Each persona can be deeply specialized, independently improved, and used in isolation.
- **Positive:** Artifact-mediated communication creates natural human checkpoints — the user reviews and approves each phase before advancing.
- **Positive:** The system is transparent — users always know which expert they're talking to and why.
- **Negative:** Phase transitions require user action (switching to a new persona/session). Mitigated by Cursor Agent Mode, which automates transitions within one session.
- **Negative:** Context must be explicitly passed between personas via artifacts. Mitigated by `PROJECT-CONTEXT.md` and the Cursor Agent's file-reading capabilities.

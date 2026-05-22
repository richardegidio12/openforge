# ADR-002: Artifact-mediated communication between personas

**Date:** 2024-03-01
**Status:** Accepted
**Context:** OpenForge design — how personas share context

---

## Context

Personas need to share context. The Data Architect must know what the Data Product Strategist decided. The Pipeline Planner must know both the architecture and the data contracts. The question is: how does this context transfer happen?

---

## Decision

Context transfers through **structured artifacts** — markdown documents with defined schemas, saved to the project folder, explicitly passed as input to the next persona. There is no direct agent-to-agent communication. The human is the intermediary.

---

## Rationale

**1. Artifacts are inspectable and correctable**
When the Data Architect produces an `architecture-document.md`, the human can read it, correct it, and approve it before it becomes input to the next phase. Direct agent-to-agent communication would skip this checkpoint — errors would propagate invisibly downstream.

**2. Artifacts are the project's memory**
When a project resumes after 3 weeks, the artifacts contain everything that was decided. A direct agent-to-agent communication system has no persistent state — context would be lost between sessions.

**3. Artifacts enable handoffs**
A new engineer joining the project reads the artifacts and gets productive quickly. A purely conversational system produces no transferable knowledge.

**4. Human checkpoint is a feature**
Data engineering decisions have real consequences (cost, compliance, security). A human approving each artifact before the next phase advances is not friction — it is accountability. The method is designed for teams that care about what they build.

**5. Artifacts are version-controllable**
Artifacts live in the project's git repository. Changes are tracked. You can see what was decided in v1.0 vs v1.1. Conversational context cannot be versioned.

---

## Alternatives considered

### Direct agent-to-agent communication (multi-agent pipeline)
- **Not rejected — deferred:** This is the natural evolution of OpenForge. Once MCP-based agent communication matures, personas could invoke each other directly. The artifact-based design is forward-compatible: the same artifacts that humans pass today could be passed programmatically tomorrow.
- **Not used in v1 because:** Adds infrastructure complexity, removes human checkpoints, reduces transparency. For v1, the method's value is the structured thinking, not the automation.

### Shared conversational context (single long conversation)
- **Partially implemented:** Cursor Agent Mode achieves this — one conversation, multiple personas, agent manages transitions. But artifacts are still generated and saved, not just held in memory.
- **Not the primary mode because:** Context windows are finite. A project with 9 personas across 4 weeks cannot fit in one context window. Artifacts survive context window limits; conversational memory does not.

---

## Consequences

- **Positive:** Every decision is documented, inspectable, and correctable.
- **Positive:** Projects can be resumed at any point — artifacts reconstruct state.
- **Positive:** The method works with any LLM and any interface (not locked to a specific tool).
- **Negative:** Phase transitions require explicit artifact passing. Mitigated by Cursor Agent Mode.
- **Negative:** Artifacts can become stale if the project changes without updating them. Mitigated by CHANGE MODE in the Orchestrator.

# ADR-005: CHANGE MODE with targeted re-evaluation over full project reruns

**Date:** 2024-03-20
**Status:** Accepted
**Context:** How OpenForge handles mid-project changes

---

## Context

Data projects change. Requirements shift. New constraints emerge. The question is: when something changes, should the method re-run all phases from the beginning, or should it intelligently identify only the affected phases and re-run those?

---

## Decision

The Orchestrator implements **CHANGE MODE** — a targeted re-evaluation that maps a described change to a Change Impact Matrix, identifies stale artifacts, and re-runs only the affected personas in the right order. It explicitly protects valid work.

---

## Rationale

**1. Full reruns destroy valid work**
If the budget changes, the architecture and pipeline spec may need revision — but the data product brief and data contracts are probably still valid. Re-running all phases from scratch wastes time, overwrites good decisions, and creates confusion about what actually changed.

**2. The Impact Matrix makes consequences explicit**
Knowing that "a change to architecture-document cascades to FinOps (revision) + Security (arch review) + Gov&Quality + Planner" is itself valuable information. Teams often change something without realizing the downstream impact. The matrix surfaces this before it becomes a problem.

**3. "What does NOT need to change" is as valuable as "what does"**
Explicitly stating that the data product brief is not affected by a budget cut (unless scope changes) prevents teams from re-opening decisions that don't need to be reopened. Scope creep through unnecessary re-evaluation is a real project risk.

**4. Projects are iterative, not linear**
The medallion architecture is itself iterative (Bronze → Silver → Gold). The method should reflect this. A method that only flows in one direction is incomplete for real projects.

---

## Alternatives considered

### Always rerun from the beginning
- **Rejected because:** Destroys valid work, demotivates teams, and ignores the fact that most changes are local, not global.

### Manual re-evaluation (user decides what to redo)
- **Rejected because:** Users don't always know the full downstream impact of a change. The Impact Matrix exists precisely to surface non-obvious cascades (e.g., an architecture change affecting the security assessment, which affects the pipeline spec).

### Event-driven propagation (automatic cascade without user approval)
- **Considered for future:** An agent that automatically re-runs affected personas when an artifact changes. Deferred to v2 because it requires agent-to-agent communication infrastructure and removes human checkpoints that are currently a deliberate feature.

---

## Consequences

- **Positive:** Changes are handled efficiently — only what needs to change, changes.
- **Positive:** The Impact Matrix is a learning tool — users understand the dependency graph of their project.
- **Positive:** Human approval at each re-evaluation step maintains accountability.
- **Negative:** The Impact Matrix must be maintained as personas are added. New personas require updating the matrix.
- **Negative:** Requires users to describe the change accurately for the Orchestrator to route correctly. Mitigated by the Orchestrator asking clarifying questions.

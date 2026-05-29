# ADR-013: Per-Persona Grill Protocol

**Date:** 2026-05-28
**Status:** Accepted
**Decided by:** OpenForge team

---

## Context

OpenForge personas produce artifacts (architecture documents, data contracts, pipeline specs, etc.) through structured conversations. However, the quality of those artifacts depends heavily on whether the underlying decisions were interrogated rigorously before being committed.

Two external skills were discovered that address this problem in software engineering contexts:
- **`grill-me`** (Matt Pocock): a structured self-interrogation protocol that probes a decision or implementation with domain-specific questions, one at a time, with a recommended answer after each.
- **`grill-with-docs`**: a variant that interrogates an existing document against a cross-reference checklist, surfacing gaps and contradictions.

The initial evaluation considered implementing a single shared `/grill` skill. However, a key insight emerged: a single generic protocol produces shallow interrogation. A Data Engineer being grilled on pipeline idempotency has completely different blind spots than a Data Architect being grilled on table format choices — or a FinOps Engineer being grilled on cost projections.

---

## Decision

**Embed a domain-specific Grill Protocol directly into each persona file**, rather than maintaining a single shared skill.

Each persona's Grill Protocol:
1. Contains **10 interrogation questions** specific to that persona's domain
2. Each question includes a **recommended answer** that reflects OpenForge standards
3. Includes a **cross-reference section** naming the specific artifacts and checks that should inform the answers
4. Contains a **domain-specific hard stop rule** — the one condition that blocks progress regardless of other answers

The protocol is activated via `/grill` (current persona) or `/grill [persona-name]` (specific persona).

A second command `/grill-docs [artifact]` activates document-review mode: read the artifact, apply the persona's cross-reference checklist, and surface findings one at a time.

---

## Interrogation dimensions by persona

| Persona | Domain focus | Hard stop condition |
|---------|-------------|---------------------|
| Data Product Strategist | Problem definition, success metrics, stakeholder alignment | No measurable success criterion |
| Data Architect | Engine choices, data model grain, ADR completeness | Decision without documented trade-offs |
| Gov & Quality Advisor | PII classification, contract completeness, quality rule coverage | PII field without a treatment decision |
| Pipeline Planner | Story granularity, dependency mapping, acceptance criteria | Story without testable acceptance criteria |
| Data Engineer | Idempotency proof, deduplication strategy, observability | Pipeline without idempotency guarantee |
| Analytics Engineer | Grain definition, metric consistency, incremental logic | Metric without a single canonical definition |
| Platform FinOps Engineer | Cost estimates, budget ceiling, idle resource detection | Budget ceiling undocumented before build |
| Security Consultant | Credential storage, SA hygiene, PII in logs | Hardcoded credential or public Bronze layer |

---

## Alternatives considered

### Option A: Single shared `/grill` skill (rejected)
A single skill with generic engineering questions (as in the original `grill-me`). Rejected because the questions would be too broad to surface persona-specific blind spots. A FinOps review asking about idempotency wastes interrogation cycles.

### Option B: Separate skill files per persona (rejected)
Keep Grill Protocols in `skills/` as separate files, referenced by personas. Rejected because it creates indirection: the protocol must be read alongside the persona anyway, and skill files can fall out of sync with the persona they serve.

### Option C: Grill as a post-artifact review step in the Orchestrator (rejected)
Have the Orchestrator automatically grill after each artifact. Rejected because grilling is most valuable *during* design, not after the artifact is already committed. It should be user-initiated, not mandatory overhead.

---

## Consequences

**Positive:**
- Each persona's interrogation is calibrated to the actual decisions it makes
- The recommended answer in each question encodes OpenForge standards without requiring separate documentation
- Cross-references tie the grill directly to project artifacts — grilling from generic knowledge is not allowed
- `/grill-docs` enables post-hoc artifact review without starting a new persona session

**Negative:**
- Maintaining 8 × 10 = 80 grill questions creates surface area for drift if personas evolve
- Questions are opinionated — a project with unusual constraints may find some questions irrelevant

**Mitigation:**
- Each grill question is a principle, not a checklist item — the persona can adapt tone to project context
- The cross-reference section anchors every grill to the actual project, reducing generic noise

---

## Implementation

All 8 persona files updated with `## Grill Protocol` section immediately before `## Activation Prompts`:

- `personas/01-data-product-strategist.md` ✅
- `personas/02-data-architect.md` ✅
- `personas/03-data-governance-quality-advisor.md` ✅
- `personas/04-pipeline-planner.md` ✅
- `personas/05-data-engineer.md` ✅
- `personas/06-analytics-engineer.md` ✅
- `personas/07-platform-finops-engineer.md` ✅
- `personas/08-security-consultant.md` ✅

Slash commands added to `.cursor/rules/openforge.mdc`:
- `/grill [persona?]` — persona-specific interrogation
- `/grill-docs [artifact]` — document cross-reference review

# ADR-004: Skills as separate, reusable modules — not embedded in personas

**Date:** 2024-03-15
**Status:** Accepted
**Context:** Design of cross-cutting technical principles

---

## Context

Technical personas (Architect, Engineer, Analytics Engineer, Planner) share a set of principles that apply across all of them: software engineering best practices, observability patterns, testing strategy, data modeling conventions. The question is where to define these principles: embedded in each persona, or as separate reusable modules.

---

## Decision

Cross-cutting principles are defined in **separate skill files** in `skills/`. Each persona that applies a skill references it explicitly in an "Applied skill" section. Skills are not duplicated across persona files.

---

## Rationale

**1. DRY — a principle change propagates from one file**
If the testing strategy evolves (e.g., a new recommendation for dbt tests), changing `skills/testing-strategy.md` updates the guidance for every persona that references it. Embedded principles would require updating 4+ persona files, with the risk of inconsistency.

**2. Skills can be added without modifying existing personas**
A new skill (e.g., `skills/privacy-by-design.md`) can be added and referenced by relevant personas without restructuring them. The skill system is open for extension.

**3. Skills are independently discoverable and usable**
A user who wants to understand OpenForge's testing philosophy can read `skills/testing-strategy.md` directly. Skills serve as standalone reference documents, not just embedded guidelines.

**4. Skills apply to Consult Mode and cursor rule too**
The `.cursor/rules/openforge.mdc` references skills directly for cross-cutting application in Consult Mode. Embedded persona principles would not be accessible to the cursor rule without duplicating them.

**5. Skills enable community specialization**
Contributors can add domain-specific skills (e.g., `skills/healthcare-compliance.md`, `skills/financial-data.md`) without touching core personas. The skill system is the extension point for domain knowledge.

---

## Alternatives considered

### Embedded in each persona (no skills directory)
- **Rejected because:** Leads to duplication and drift. When the software engineering principles evolve, maintaining consistency across 4+ persona files is error-prone.

### Single cross-cutting principles document
- **Considered:** A single `PRINCIPLES.md` that all personas reference. Rejected because different personas apply different subsets of skills at different depths. A monolithic principles file doesn't allow personas to reference only what's relevant to them.

### Skills embedded in the cursor rule only
- **Rejected because:** Skills should be available in manual LLM mode (without Cursor) as well. The cursor rule references skills; the skills themselves must exist as standalone documents.

---

## Consequences

- **Positive:** Single source of truth for each cross-cutting principle.
- **Positive:** Skills can be added, updated, or removed without touching persona files.
- **Positive:** Skills are independently readable as reference documents.
- **Negative:** Personas reference skill files that users must understand exist. Mitigated by explicit "Applied skill" sections in each persona.
- **Negative:** A skill update requires verifying that all referencing personas still apply it correctly. Mitigated by keeping skill references explicit (not implicit).

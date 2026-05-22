# ADR-003: FinOps and Security as transversal personas, not phase gates

**Date:** 2024-03-10
**Status:** Accepted
**Context:** Design of personas 07 (FinOps) and 08 (Security)

---

## Context

Cost and security are concerns that arise at multiple points in a data project — not just at one specific phase. The question is whether to model them as phase-specific gates (mandatory checkpoints) or as transversal advisors (available at any phase, multiple modes).

---

## Decision

Platform FinOps Engineer (07) and Security Consultant (08) are **transversal personas** with multiple modes. They can be invoked at any phase. They inform and alert — they do not block or veto decisions.

---

## Rationale

**1. Cost and security are not one-time concerns**
A budget constraint discovered after the architecture is finalized should trigger a revision. A new data source added mid-build should trigger a security review. Making these concerns phase-specific would mean they're only applied once, at the "wrong" moment for many real projects.

**2. "Cost is context, not veto" — FinOps philosophy**
A 2-person team with a $300/month budget and a 5-person team with no limit should get different recommendations, not blocked decisions. The FinOps persona surfaces cost implications so the team can make informed trade-offs. The decision remains with the team.

**3. Security for small teams must be practical, not theoretical**
A mandatory security gate that produces a 40-page compliance report for a 2-person team will be ignored. The Security Consultant is calibrated to team size — concrete, implementable findings, not enterprise theater. Making it optional per context encourages actual use.

**4. Transversal design enables the CHANGE MODE integration**
When something changes (new source, architecture revision, budget cut), the Change Impact Matrix maps the change to the relevant transversal personas. A phase-specific gate can't participate in mid-project re-evaluation naturally.

---

## Alternatives considered

### Fixed phase gates (mandatory at specific phases)
- **Rejected because:** Real projects don't follow a linear sequence. Budget constraints emerge mid-architecture. Security gaps are found during build. Rigid gates create the illusion of safety without the substance.

### Integrated into existing personas (no separate FinOps/Security personas)
- **Rejected because:** Cost and security reasoning are deep enough to warrant dedicated expertise. A Data Architect who must also be a FinOps expert and a Security Consultant produces shallow output in all three dimensions. Specialization wins.

### Separate personas per mode (FinOps-Context, FinOps-Revision, Security-Arch, Security-Audit)
- **Rejected because:** Adds complexity without proportional value. A single persona with multiple modes is cognitively simpler for the user and easier to maintain as a single file.

---

## Consequences

- **Positive:** FinOps and Security are available at any point in the project, not just at predefined checkpoints.
- **Positive:** Multiple modes per persona match the different contexts where cost/security thinking is needed.
- **Positive:** Non-blocking design means recommendations are taken seriously rather than worked around.
- **Negative:** Transversal personas require the Orchestrator to know when to invoke them. This adds routing complexity to the Orchestrator.
- **Negative:** "Not mandatory" could mean teams skip them. Mitigated by Orchestrator routing logic that prompts for FinOps when no `cost-context.md` exists, and for Security when PII is present and `security-assessment.md` is missing.

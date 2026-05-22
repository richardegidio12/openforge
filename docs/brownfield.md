# Using OpenForge on an Existing Project

How OpenForge behaves when cloned into a project that already has its own SDD artifacts — ADRs, architecture docs, decision logs, specs, or prior BMAD sessions.

---

## The core principle

OpenForge **reads and respects** existing decisions. It does not start from scratch, does not override prior choices, and does not treat the project as a blank canvas.

When existing SDD is found:
- Decisions already made are **locked** — the agent follows them, it doesn't re-evaluate them
- Gaps vs OpenForge standards are surfaced as **opportunities**, not failures
- Conflicts with existing decisions are surfaced as **questions**, not blockers

---

## What happens on first entry

When OpenForge is cloned into a project that has no `PROJECT-CONTEXT.md`, it automatically runs the **SDD Discovery** before doing anything else.

You can also trigger it explicitly at any time:

```
/scan
```

### Discovery Report

The agent scans for SDD artifacts across common formats and locations:

| What it looks for | Examples |
|-------------------|---------|
| Architecture Decision Records | `docs/decisions/ADR-*.md`, `docs/adr/*.md`, `adr/*.md` |
| Specification files | `SPEC.md`, `ARCHITECTURE.md`, `DESIGN.md`, `TECHNICAL_SPEC.md` |
| RFC / proposals | `docs/rfcs/**`, `proposals/**` |
| Decision logs | `DECISIONS.md`, entries in `CHANGELOG.md` |
| BMAD artifacts | `docs/prd.md`, `docs/stories/**`, `.ai/**`, `bmad-core/**` |
| OpenForge artifacts | `data-product-brief.md`, `architecture-document.md`, etc. |

Then it produces a Discovery Report like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SDD DISCOVERY — orders-platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 7 existing SDD artifacts. Mapping to OpenForge phases:

✅ Phase 1 (Discovery)     → docs/prd.md (BMAD format, complete)
✅ Phase 2 (Architecture)  → ARCHITECTURE.md + docs/adr/ (3 ADRs)
❌ Phase 2.5 (FinOps)      → not found — no cost budget documented
⚠️ Phase 2.6 (Security)    → docs/security-review-2023.md (outdated — predates PII source)
❌ Phase 3 (Contracts)     → not found — no data contracts
❌ Phase 4 (Planning)      → partial — GitHub issues exist but no pipeline-spec
...

📋 Existing decisions locked (will not be overridden):
- ADR-001: Delta Lake over Iceberg (Databricks primary stack)
- ADR-002: Airflow on EKS for orchestration
- ADR-003: Single service account for all pipeline components ⚠️ (see conflicts)

⚠️ Potential gaps vs OpenForge standards:
- No data contracts — quality rules are undocumented and untestable
- Security review is 8 months old — new PII source (customer_email) not assessed
- No cost budget documented — FinOps recommendations will be unconstrained

⚠️ Conflicts requiring attention:
- ADR-003 (single SA) creates privilege escalation risk — Security Consultant can review

🚀 Suggested entry point:
Your architecture is defined. Recommended next step: Phase 3 (Governance & Contracts)
with the Data Gov & Quality Advisor, using ARCHITECTURE.md + docs/prd.md as input.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## How locked decisions work

Once a decision is found in your existing SDD, it is **locked** for this session. The agent will not contradict it.

**What "locked" means in practice:**

Your project has `ADR-001: Use Delta Lake`. OpenForge's decision tree would normally recommend Iceberg for a multi-engine setup — but it won't here. Instead:

```
📌 Using Delta Lake — locked by ADR-001 (docs/adr/ADR-001.md).
   OpenForge default would be Iceberg for multi-engine queries,
   but your ADR documents the Databricks dependency that justifies Delta.
```

The agent follows your decision, notes the default it would have chosen, and moves on.

**When does a locked decision get flagged anyway?**

Only when it creates a **measurable risk** the original author may not have considered — a security vulnerability, a known operational failure mode, or a constraint that has since changed. Even then, it's flagged as a question, not overridden:

```
⚠️ CONFLICT DETECTED
Locked decision: Single service account for all components (ADR-003)
Risk: Privilege escalation — if compromised, all pipeline access is exposed
Options: A) Accept with documented risk  B) Review now (/security)  C) Defer to Open Items
```

---

## Mapping BMAD to OpenForge

If the project used BMAD before OpenForge, here's how artifacts map:

| BMAD artifact | OpenForge equivalent | What to do |
|--------------|---------------------|------------|
| `docs/prd.md` | `data-product-brief.md` | Read as Phase 1 input — don't regenerate |
| `docs/architecture.md` | `architecture-document.md` | Read as Phase 2 input |
| `docs/stories/*.md` | `pipeline-spec.md` | Partial equivalent — Planner can formalize |
| BMAD ADRs | OpenForge ADRs | Lock as existing decisions |
| No equivalent | `data-contract-*.md` | Gap — Phase 3 needed |
| No equivalent | `cost-context.md` | Gap — Phase 2.5 needed |
| No equivalent | `security-assessment.md` | Gap — Phase 2.6 needed |

---

## Typical brownfield entry paths

### "The project has architecture docs but no contracts or quality rules"

```
/scan
→ Discovery shows Phase 1+2 covered, Phase 3 missing
→ Activate: /gov
→ Gov & Quality reads existing ARCHITECTURE.md + prd.md
→ Produces: data-contract-[name].md + governance-policy.md
```

### "The project has an old security review that predates new data sources"

```
/scan
→ Discovery flags security-review.md as outdated
→ Activate: /security
→ Security reads architecture + old review + new sources
→ Produces: updated security-assessment.md with delta from prior review
```

### "The project has everything but we want to validate it against OpenForge standards"

```
/party-mode Is our current architecture and process production-ready?
→ Every persona reviews what exists from their domain
→ Gaps, risks, and missing artifacts surfaced in synthesis
→ Prioritized list of what to address before production
```

### "We used BMAD — we want to continue with OpenForge"

```
/scan
→ BMAD artifacts detected and mapped
→ Discovery Report shows which OpenForge phases are covered
→ Agent offers to bootstrap PROJECT-CONTEXT.md from existing artifacts
→ Continue from the first uncovered phase
```

---

## PROJECT-CONTEXT.md bootstrap

After a `/scan`, the agent offers to create `PROJECT-CONTEXT.md` pre-filled with everything it found:
- Decision Anchors extracted from ADRs and architecture docs
- Key Decisions imported from existing ADRs
- Artifact status table (what exists, what's missing)
- Suggested next phase

This means **future sessions start in seconds** — the discovery only needs to happen once.

---

## What OpenForge will NOT do on an existing project

- **Not override existing technology choices** — if you chose Airflow 2 years ago and it's working, OpenForge won't recommend switching to Dagster unless you ask
- **Not re-run phases that are already covered** — if you have a solid architecture document, OpenForge won't redo Phase 2 from scratch
- **Not ignore existing code** — in CONSULT MODE, the agent reads your actual pipeline code, not just the SDD artifacts
- **Not add ceremony to a working project** — if you're a POC with no PII heading to production in a week, OpenForge calibrates to that context

# OpenForge: Full Project Workflow
> Open Framework for Orchestrated and Reliable data-platform Generation & Engineering

---

## Philosophy

Small and medium data teams fail not from lack of technology, but from lack of **structured thinking**. OpenForge solves this by introducing specialized personas that guide each project phase — from understanding the problem all the way to production delivery with quality, governance, and security in place.

Each persona is a **mode of reasoning**, not a job title. A single person can (and often will) engage with multiple personas in sequence.

Two personas — **FinOps Engineer** and **Security Consultant** — are **transversal**: they can be called at any point in the project, not just at a fixed phase.

---

## Workflow Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        OPENFORGE WORKFLOW                            │
└──────────────────────────────────────────────────────────────────────┘

  ENTRY POINT
  ────────────
  Orchestrator (00) ← always start here
       │
       ▼ Mission Plan

  PHASE 1             PHASE 2             PHASE 2.5 / 2.6
  DISCOVERY           ARCHITECTURE        TRANSVERSAL
  ─────────           ────────────        ────────────────
  Data Product    →   Data            →   💰 FinOps Eng. (cost context)
  Strategist          Architect       →   🔒 Security Consultant (arch review)
       │                   │                    │
       ▼                   ▼                    ▼
  data-product-      architecture-       cost-context.md
  brief.md           document.md         security-assessment.md


  PHASE 3             PHASE 4             PHASE 5
  GOVERNANCE          PLANNING            BUILD
  ──────────          ────────            ─────
  Gov & Quality   →   Pipeline        →   Data Engineer
  Advisor             Planner             + Analytics Eng.
  (contract)               │                    │
       │                   ▼                    ▼
       ▼              pipeline-spec.md     Code + tests
  data-contract.md                         + runbooks
  governance-
  policy.md


  PHASE 6             PHASE 6.5
  VALIDATION          SECURITY AUDIT
  ──────────          ──────────────
  Gov & Quality   →   Security
  Advisor             Consultant
  (validation)        (pre-prod audit)
       │                    │
       ▼                    ▼
  quality-            security-
  signoff.md          signoff.md


  ──────────────────────────────────────────────
  AT ANY POINT: call Orchestrator in CHANGE MODE
  when scope, budget, stack, or requirements change
  ──────────────────────────────────────────────
```

---

## Phase 0 — Orchestration (always the entry point)

**Persona:** `Orchestrator`
**Goal:** Diagnose project state and deliver a precise Mission Plan.

The Orchestrator operates in two modes:

**START / RESUME MODE** — called at project start or when resuming after a break:
- Asks which artifacts already exist
- Routes to the right persona with activation instructions
- Delivers a full estimated sequence

**CHANGE MODE** — called when something changes mid-project:
- User describes the change (new source, budget cut, PII found, scope shift)
- Orchestrator maps the change against the Impact Matrix
- Identifies which artifacts are stale and which personas need re-evaluation
- Explicitly states what does NOT need to change (protects valid work)
- Delivers a targeted Change Mission Plan with impact level 🟢/🟡/🔴

### When to invoke
Always — at project start, session resume, scope change, routing doubt, or mid-project discovery.

---

## Phase 1 — Discovery

**Persona:** `Data Product Strategist`
**Goal:** Understand the business problem before any technical decision.

### Key questions answered
- What business problem are we solving?
- Who are the consumers of this data? (analysts, dashboards, ML models, APIs)
- What decisions will this data enable?
- What metrics/KPIs need to exist?
- What data sources are available?
- What is the expected update frequency?
- What is the cost of incorrect or delayed data?

### Artifact produced
**`data-product-brief.md`** — structured document capturing business problem, consumers, sources, success criteria, and constraints.

### Exit criterion
Brief validated with the business stakeholder. Clear problem defined before any technical decision.

> **Never skip Phase 1.** Data built for the wrong problem is worse than no data at all.

---

## Phase 2 — Architecture

**Persona:** `Data Architect`
**Input:** `data-product-brief.md`
**Goal:** Define the simplest technical architecture that solves the problem.

### Key questions answered
- What is the data volume and velocity? (batch vs streaming)
- What is the storage strategy? (Data Lakehouse, DW, hybrid)
- Which layers make sense? (Bronze/Silver/Gold or simpler)
- Which orchestrator? (Airflow, Dagster, Prefect, simple cron)
- What is the transformation stack? (dbt, Spark, plain SQL, pandas)
- What are the cost and time-to-market constraints?
- How will data be consumed? (BI tool, API, feature store)

### Guiding principle
> "The right architecture for a 3-person team is different from the right one for a 30-person team. Simplicity is a feature."

### Artifact produced
**`architecture-document.md`** — justified technical decisions (ADRs), data flow diagram, chosen stack, cost estimate.

### Exit criterion
Architecture reviewed by the technical team. Key trade-offs documented as ADRs.

---

## Phase 2.5 — Cost Context *(transversal — recommended before architecture is finalized)*

**Persona:** `Platform FinOps Engineer`
**Input:** conversation + architecture draft (if available)
**Goal:** Establish budget constraints and classify the financial restriction level before technical decisions are locked in.

### Philosophy
> "Cost is context, not veto."

The FinOps Engineer informs decisions. It does not block the project. It makes financial constraints visible so the team can make conscious trade-offs.

### Modes
- **Context Mode** — establishes budget baseline → produces `cost-context.md` with 🟢/🟡/🔴 restriction level
- **Revision Mode** — reviews ADRs with cost estimates and alternatives (called alongside Data Architect)
- **Audit Mode** — post-production billing review → produces `finops-audit.md`

### Artifact produced
**`cost-context.md`** — budget constraints, restriction level, cost guardrails that feed all other personas.

### Exit criterion
Budget constraint documented. Restriction level clear to the team.

---

## Phase 2.6 — Security Assessment *(transversal — required if PII is present or project goes to production)*

**Persona:** `Security Consultant`
**Input:** `architecture-document.md`
**Goal:** Identify security gaps before contracts or build start.

### Philosophy
> "Practical security for small teams: achievable, not theoretical."

The Security Consultant calibrates to team size. A 2-person team doesn't need enterprise SIEM. Recommendations are concrete and implementable.

### Modes
- **Architecture Review Mode** — security posture review → produces `security-assessment.md`
- **Implementation Guidance Mode** — per-story patterns (secrets, IAM, logging) during build
- **Pre-production Audit Mode** — final checklist before go-live → produces `security-signoff.md`

### Pillars assessed
1. **IAM & Least Privilege** — service accounts, roles, layer access
2. **Secrets & Credentials** — secrets manager, no hardcoded values, rotation
3. **Encryption** — at rest, in transit, column-level for PII
4. **Network Isolation** — VPCs, private endpoints, no unnecessary public exposure

### Artifact produced
**`security-assessment.md`** — findings classified as 🔴 Critical / 🟡 Important / 🟢 Recommended, plus SEC-XXX stories to add to the pipeline spec.

### Exit criterion
No 🔴 Critical items open (or explicitly accepted with documented justification).

> ⚠️ For POCs with no PII and no production target, this phase can be deferred. Document the deferral.

---

## Phase 3 — Governance & Quality

**Persona:** `Data Governance & Quality Advisor` (Contract Mode)
**Input:** `data-product-brief.md` + `architecture-document.md`
**Goal:** Define contracts, ownership, and quality expectations BEFORE building.

### Boundary with Security Consultant
- **Gov & Quality owns:** *what* is PII, *what the rules are*, data contracts, quality SLAs, retention policy
- **Security Consultant owns:** *who can access* PII, *how it is encrypted*, audit logging

### Key questions answered

**Governance:**
- Who is the owner of each dataset?
- Who can read? Who can write?
- Are there PII fields? How will they be handled? (LGPD/GDPR)
- How will this data be cataloged and documented?
- What is the retention policy?

**Quality:**
- What is the expected schema for each table/topic?
- What is the freshness SLA? (e.g. "data must be updated within 2h of the event")
- What are the completeness expectations?
- What are the uniqueness expectations?
- How to alert when quality drops?

### Artifacts produced
- **`data-contract-[name].md`** — one contract per dataset/domain
- **`governance-policy.md`** — ownership, access, PII treatment, retention

### Exit criterion
Contracts signed (even informally) by owners. Quality rules documented before the first commit.

---

## Phase 4 — Implementation Planning

**Persona:** `Pipeline Planner`
**Input:** all previous artifacts
**Goal:** Break the project into concrete, sequenced engineering stories.

### What the Pipeline Planner does
- Identifies engineering stories (epics → stories)
- Incorporates SEC-XXX stories from `security-assessment.md`
- Defines implementation order (pipeline dependencies)
- Estimates effort per story
- Identifies technical risks before build
- Defines acceptance criteria for each story

### Standard epic structure
```
Epic 0 — Setup and Infrastructure
Epic 1 — Ingestion (Bronze)
Epic 2 — Transformation and Cleaning (Silver)
Epic 3 — Modeling and Serving (Gold)
Epic 4 — Quality and Monitoring
Epic 5 — Governance and Documentation
```

### Artifact produced
**`pipeline-spec.md`** — complete story backlog with acceptance criteria, effort estimates, dependencies, and sequencing.

### Exit criterion
Team aligned on delivery sequence. All stories have clear acceptance criteria.

---

## Phase 5 — Build

**Personas:** `Data Engineer` + `Analytics Engineer`
**Input:** `pipeline-spec.md` + all previous artifacts
**Goal:** Implement story by story, respecting the defined contracts.

> These personas are activated **per story or epic**, not once for the full build.

### Data Engineer — Epics 0, 1, 2 (and 4, 5)
- Connectors and ingestion (APIs, databases, files, events)
- Bronze layer: raw data, no transformation, with ingestion metadata
- Silver layer: cleaning, typing, deduplication, PII anonymization
- Orchestrator configuration (DAGs, schedules, retries, alerts)
- Infrastructure provisioning (IaC)
- Security patterns: secrets injection, SA hygiene, safe logging

### Analytics Engineer — Epic 3 (and 4, 5)
- Gold layer: dimensional modeling, aggregations, business metrics
- dbt models (staging → intermediate → marts)
- Semantic layer (if applicable)
- Model documentation (dbt docs)
- Transformation tests

### Guiding principle
> "A story is only done when the data is correct, tested, documented, and monitored. There is no 'works on my machine' in data."

### Exit criterion per story
- [ ] Pipeline runs without errors
- [ ] Quality tests passing (per data contract)
- [ ] Documented (schema, description, owner)
- [ ] Monitoring and alerts configured
- [ ] No secrets in code or logs
- [ ] Code review approved

---

## Phase 6 — Final Validation

**Persona:** `Data Governance & Quality Advisor` (Validation Mode)
**Input:** implemented pipelines + `data-contract-[name].md`
**Goal:** Ensure that what was built respects what was promised.

### Validation checklist

**Quality:**
- [ ] All data contract tests implemented and passing?
- [ ] Freshness SLA being monitored?
- [ ] Alerts configured and tested?
- [ ] Lineage documented and traceable?

**Governance:**
- [ ] PII fields correctly treated (anonymized/removed per contract)?
- [ ] Access controls applied?
- [ ] Dataset cataloged with owner and description?
- [ ] Owner notified and sign-off obtained?

### Artifact produced
**`quality-signoff.md`** — filled checklist with ✅/⚠️/❌ classifications, deviations documented, technical debt recorded.

---

## Phase 6.5 — Security Audit *(required before production)*

**Persona:** `Security Consultant` (Pre-production Audit Mode)
**Input:** `architecture-document.md` + `security-assessment.md`
**Goal:** Confirm the build implements the security baseline before going live.

### Final checklist covers
- IAM: all SAs follow least privilege, Bronze restricted, Gold read-only for analysts
- Secrets: no credentials in code, all in secrets manager, `profiles.yml` not committed
- Encryption: at rest confirmed, all connections TLS
- Network: no unnecessary public endpoints, BI tool via private connection
- Audit logging: enabled on production datasets, no PII in pipeline logs

### Artifact produced
**`security-signoff.md`** — checklist with ✅/⚠️/❌, accepted risks documented, next review date.

### Sign-off status
- ✅ **Approved** — zero 🔴 Critical items open
- ⚠️ **Approved with accepted risks** — no Critical items, Important items documented
- ❌ **Not approved** — any Critical item open → do not go to production

---

## Summary: All Artifacts by Phase

| Phase | Persona | Artifact |
|-------|---------|----------|
| 0 — Orchestration | Orchestrator | Mission Plan (not saved) |
| 1 — Discovery | Data Product Strategist | `data-product-brief.md` |
| 2 — Architecture | Data Architect | `architecture-document.md` |
| 2.5 — Cost Context | Platform FinOps Engineer | `cost-context.md` |
| 2.6 — Security Assessment | Security Consultant | `security-assessment.md` |
| 3 — Governance | Gov & Quality Advisor | `data-contract-[name].md` + `governance-policy.md` |
| 4 — Planning | Pipeline Planner | `pipeline-spec.md` |
| 5 — Build | Data Engineer + Analytics Eng. | Code + tests + runbooks |
| 6 — Validation | Gov & Quality Advisor | `quality-signoff.md` |
| 6.5 — Security Audit | Security Consultant | `security-signoff.md` |

---

## Recommended project folder structure

```
my-project/
├── data-product-brief.md        ← Phase 1
├── architecture-document.md     ← Phase 2
├── cost-context.md              ← Phase 2.5
├── security-assessment.md       ← Phase 2.6
├── governance-policy.md         ← Phase 3
├── data-contract-[dataset].md   ← Phase 3 (one per dataset)
├── pipeline-spec.md             ← Phase 4
├── quality-signoff.md           ← Phase 6
├── security-signoff.md          ← Phase 6.5
└── docs/
    └── runbooks/                ← Phase 5 (one per pipeline)
```

---

## When to skip phases

| Scenario | Adaptation |
|----------|------------|
| POC / exploration | Phases 1+2 combined, Phase 2.6 deferred (no PII, no prod), Phase 3 informal |
| Internal pipeline, no external consumers | Phase 3 simplified (informal contract) |
| Maintaining an existing pipeline | Jump to Phase 4; invoke Security if schema or access changes |
| Solo engineer | Same personas, one person engages all of them |
| Budget unknown | Run Phase 2.5 before Phase 1 to establish constraints first |

> **Golden rule: never skip Phase 1.** Data built for the wrong problem is worse than no data at all.

---

## CHANGE MODE — iterative re-evaluation

Projects are not linear. Requirements change. New sources are discovered. Budgets are cut. PII is found late. **CHANGE MODE** handles this.

When something changes, call the Orchestrator and describe the change. It will:
1. Map the change to the **Change Impact Matrix**
2. Identify which artifacts are now stale
3. Deliver a targeted Mission Plan — only the affected personas, in order
4. Explicitly state what does **not** need to change

**Change Impact Matrix (summary):**

| What changed | Re-evaluate |
|-------------|-------------|
| `data-product-brief` | Architect → Security → Gov&Quality → Planner |
| `architecture-document` | FinOps (Revision) → Security (Arch Review) → Gov&Quality → Planner |
| Budget cut | Architect (ADR review) → Planner (story scope) |
| New data source | Security (partial) → Gov&Quality (new contract) → Planner (new stories) |
| PII found late | Security (URGENT) → Gov&Quality (URGENT) → Data Engineer (fix) |
| Security incident | Security (Arch Review) → Data Engineer (rotate, audit) → security-signoff (re-issue) |
| Quality issue in production | Gov&Quality (contract update) → Planner (remediation stories) |

See `personas/00-orchestrator.md` for the full matrix and Change Mission Plan format.

---

## Persona reference

| # | Persona | File | Type |
|---|---------|------|------|
| 00 | Orchestrator | `personas/00-orchestrator.md` | Entry point |
| 01 | Data Product Strategist | `personas/01-data-product-strategist.md` | Phase 1 |
| 02 | Data Architect | `personas/02-data-architect.md` | Phase 2 |
| 03 | Data Gov & Quality Advisor | `personas/03-data-governance-quality-advisor.md` | Phase 3 + 6 |
| 04 | Pipeline Planner | `personas/04-pipeline-planner.md` | Phase 4 |
| 05 | Data Engineer | `personas/05-data-engineer.md` | Phase 5 |
| 06 | Analytics Engineer | `personas/06-analytics-engineer.md` | Phase 5 |
| 07 | Platform FinOps Engineer | `personas/07-platform-finops-engineer.md` | Transversal |
| 08 | Security Consultant | `personas/08-security-consultant.md` | Transversal |

See: [`/personas/`](../personas/) for activation prompts and full persona instructions.

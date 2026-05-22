# How to Use OpenForge

Quick-start guide for running your first project with the method.

---

## What you'll need

- An LLM of your choice (Claude, ChatGPT, Gemini — works with any)
- The files from this repository open in your editor
- ~15 minutes for the first session (Orchestrator)

No installation required. The method is based on structured conversations.

---

## How it works in one paragraph

You open a conversation with an LLM, paste a persona's activation prompt, it conducts a structured interview with you and generates a document at the end. You save that document, open a new conversation with the next persona, pass the document as context and repeat. Each persona consumes what the previous one produced.

---

## Where to start — always with the Orchestrator

Don't know which persona to use? Doesn't matter where you are in the project. **Always start with the Orchestrator.**

1. Open [`personas/00-orchestrator.md`](personas/00-orchestrator.md)
2. Copy the **"Activation Prompt"** at the end
3. Paste it into a new LLM conversation
4. Answer the diagnostic questions
5. Receive the **Mission Plan** — which persona to use, in which order, with exact instructions

The Orchestrator can be called at any time: project start, resuming after a break, scope change, or simply "what do I do next?"

---

## Step-by-step for each phase

### PHASE 1 — Discovery
**Persona:** Data Product Strategist | **Time:** 30–60 min

1. Open [`personas/01-data-product-strategist.md`](personas/01-data-product-strategist.md)
2. Copy the **Activation Prompt** at the end
3. Paste into a new LLM conversation and answer the questions
4. Ask: *"Now generate the data-product-brief.md"*
5. Save to `my-project/data-product-brief.md`

**Exit criterion:** clear business problem, identified consumers, defined success criterion.

---

### PHASE 2 — Architecture
**Persona:** Data Architect | **Time:** 45–90 min

1. Open [`personas/02-data-architect.md`](personas/02-data-architect.md)
2. Copy the **Activation Prompt**, paste into new chat
3. Add below it: full content of `data-product-brief.md`
4. Answer questions about stack, volume and latency
5. Save output to `my-project/architecture-document.md`

**Exit criterion:** technical decisions documented with justification (ADRs), stack defined.

---

### PHASE 2.5 — Cost Context *(recommended before architecture is finalized)*
**Persona:** Platform FinOps Engineer (Context Mode) | **Time:** 15–20 min

1. Open [`personas/07-platform-finops-engineer.md`](personas/07-platform-finops-engineer.md)
2. Copy the **Activation Prompt — Context Mode**
3. Answer the financial context questions (max 6)
4. Save output to `my-project/cost-context.md`

**Exit criterion:** budget constraints documented with 🟢/🟡/🔴 restriction level.

---

### PHASE 2.6 — Security Assessment *(required if PII is present or project goes to production)*
**Persona:** Security Consultant (Architecture Review Mode) | **Time:** 30–45 min

1. Open [`personas/08-security-consultant.md`](personas/08-security-consultant.md)
2. Copy the **Activation Prompt — Architecture Review Mode**
3. Paste into a new LLM conversation
4. Add: content of `architecture-document.md`
5. Save output to `my-project/security-assessment.md`
6. Add SEC-XXX stories from the assessment to `pipeline-spec.md` (done in Phase 4)

**Exit criterion:** security posture assessed across all 4 pillars, no 🔴 Critical items open (or explicitly accepted with justification).

> ⚠️ For POCs with no PII and no production target, this phase can be deferred. Document the deferral.

---

### PHASE 3 — Governance & Contracts
**Persona:** Data Gov & Quality Advisor (Contract Mode) | **Time:** 45–60 min

1. Open [`personas/03-data-governance-quality-advisor.md`](personas/03-data-governance-quality-advisor.md)
2. Copy the **Activation Prompt — Contract Mode**
3. Add: content of `data-product-brief.md` + `architecture-document.md`
4. Answer questions about ownership, PII and quality
5. Save: `my-project/data-contract-[name].md` + `my-project/governance-policy.md`

**Exit criterion:** every dataset has an owner, PII identified with treatment, quality rules are testable.

---

### PHASE 4 — Planning
**Persona:** Pipeline Planner | **Time:** 60–90 min

1. Open [`personas/04-pipeline-planner.md`](personas/04-pipeline-planner.md)
2. Copy the **Activation Prompt**
3. Add: content of ALL previous documents
4. Answer questions about environment, sources and team
5. Save output to `my-project/pipeline-spec.md`

**Exit criterion:** backlog with concrete stories, verifiable acceptance criteria, sequencing defined.

---

### PHASE 5 — Build
**Personas:** Data Engineer + Analytics Engineer
> Activated **per story**, not once. Call them whenever you need guidance on a specific story.

- **Data Engineer** → Epics 0, 1, 2 (setup, ingestion, Silver)
- **Analytics Engineer** → Epic 3 (Gold, dbt models, marts)

For both: open the persona file, copy the activation prompt, add `pipeline-spec.md` + relevant `data-contract.md`, and tell it which story you're working on.

**Exit criterion per story:** code + tests + monitoring + documentation.

---

### PHASE 6 — Final Validation
**Persona:** Data Gov & Quality Advisor (Validation Mode) | **Time:** 30–60 min

1. Open [`personas/03-data-governance-quality-advisor.md`](personas/03-data-governance-quality-advisor.md)
2. Copy the **Activation Prompt — Validation Mode**
3. Add: `data-contract-[name].md` from Phase 3
4. Walk through the checklist with the responsible engineer
5. Save output to `my-project/quality-signoff.md`

**Exit criterion:** quality-signoff with "Approved" or "Approved with caveats" (debts documented).

---

### PHASE 6.5 — Security Audit *(required before production)*
**Persona:** Security Consultant (Pre-production Audit Mode) | **Time:** 30–45 min

1. Open [`personas/08-security-consultant.md`](personas/08-security-consultant.md)
2. Copy the **Activation Prompt — Pre-production Audit Mode**
3. Add: `architecture-document.md` + `security-assessment.md`
4. Walk through the security checklist
5. Save output to `my-project/security-signoff.md`

**Exit criterion:** security-signoff with "Approved" or "Approved with accepted risks" — zero 🔴 Critical items open.

---

## Recommended project folder structure

```
my-project/
├── PROJECT-CONTEXT.md           ← session compaction (created after Phase 1)
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

## Quick reference

| Phase | Persona | File | Receives | Produces |
|-------|---------|------|----------|---------|
| — | Orchestrator | `00-orchestrator.md` | project context | Mission Plan |
| 1 | Data Product Strategist | `01-...md` | nothing | brief |
| 2 | Data Architect | `02-...md` | brief | architecture |
| 2.5 | Platform FinOps Engineer | `07-...md` | conversation | cost-context |
| 2.6 | Security Consultant | `08-...md` | architecture | security-assessment |
| 3 | Gov & Quality (Contract) | `03-...md` | brief + architecture | contract + policy |
| 4 | Pipeline Planner | `04-...md` | everything above | pipeline-spec |
| 5a | Data Engineer | `05-...md` | spec + contract | code + runbook |
| 5b | Analytics Engineer | `06-...md` | spec + brief + contract | dbt models + docs |
| 6 | Gov & Quality (Validation) | `03-...md` | contract | quality-signoff |
| 6.5 | Security Consultant | `08-...md` | architecture + security-assessment | security-signoff |

---

## Shortcuts by scenario

| Scenario | What to do |
|----------|-----------|
| Quick POC | Phases 1+2 combined, skip Phase 3, Epics 1 and 3 only |
| Maintaining an existing pipeline | Skip Phases 1–3, start at Phase 4 |
| Solo engineer | All phases, one person talks to all personas |
| Contracts for a legacy dataset | Phase 3 (Contract) + Phase 6 (Validation) only |
| **Existing project with SDD** | Run `/scan` — OpenForge maps what exists, locks prior decisions, identifies gaps, and suggests entry point |
| **Migrating from BMAD** | Run `/scan` — BMAD artifacts are detected and mapped to OpenForge phases automatically |
| **Validating a project before production** | `/party-mode Is our project production-ready?` — all personas review from their domain |

---

## Managing context across sessions

Real projects span days or weeks. The `PROJECT-CONTEXT.md` artifact is designed to solve this.

### What it is

A compact (~100 lines) summary of your project that any agent can read in seconds. It contains:
- Current phase and next action
- Stack and team size
- Status table for every artifact (✅ Approved / 🔄 Draft / ⏳ Pending / ❌ Stale)
- Key Decisions log (append-only — decisions made are never deleted)
- Open items and blockers
- Session log (last 5 sessions)

### When to use it

| Scenario | What to do |
|----------|-----------|
| Resuming after days or weeks | Paste `PROJECT-CONTEXT.md` into new chat before activation prompt |
| Handing off to another engineer | Share `PROJECT-CONTEXT.md` — they're up to speed immediately |
| Long session hitting context limits | Ask agent to "save context" — it updates the file and you can start fresh |
| Managing multiple projects | Each project folder has its own `PROJECT-CONTEXT.md` |

### How to create it

1. Copy `templates/project-context.md` to your project folder
2. Fill in Quick State and Stack manually, or ask an agent to fill it after Phase 1
3. From then on, the agent updates it automatically at each session end (Cursor Agent Mode)
4. For manual mode: ask the persona to "update PROJECT-CONTEXT.md" before ending the session

### How to resume a session

In a new conversation, paste:
```
[activation prompt for the Orchestrator or relevant persona]

---

[full content of PROJECT-CONTEXT.md]
```

The agent reads the context and picks up exactly where you left off.

---

## Slash commands

In Cursor Agent Mode (or any LLM that has loaded the OpenForge rule), you can type `/command` at the start of any message to trigger a specific behavior immediately.

**Call a persona directly:**
```
/architect   /finops   /security   /gov   /planner   /engineer   /dbt
```

**Trigger a mode:**
```
/change We're replacing Airflow with Dagster — what artifacts need updating?
/consult Why is the Silver pipeline 3x slower than last month?
/review architecture-document.md
```

**Utility and analysis:**
```
/status                         → current project state
/brainstorm pipeline resilience → free exploration
/compare Iceberg vs Delta       → side-by-side for your project
/risk external data access      → risk identification
/adr storage format decision    → draft an ADR
/recap                          → session summary
```

**Full reference:** [`docs/slash-commands.md`](docs/slash-commands.md)

---

## Tips

- **Paste full documents** — don't summarize, more context = better output
- **Validate the summary** — every persona confirms its understanding before generating the artifact
- **One chat per persona** — don't mix personas in the same conversation (unless using Cursor Agent Mode)
- **Iterate on artifacts** — they are living documents, go back and update when needed
- **Save everything** — artifacts are the project's memory, PROJECT-CONTEXT.md is the project's brain

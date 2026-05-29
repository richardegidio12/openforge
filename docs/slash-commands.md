# OpenForge Slash Commands

Quick-reference for all `/commands` available in any OpenForge session (Cursor Agent Mode or any LLM that has loaded the `.cursor/rules/openforge.mdc`).

Type a command at the start of your message. It takes effect immediately — no confirmation needed.

---

## Operating mode commands

OpenForge operates in one of three explicit modes. Modes persist until changed.

| Command | Marker | What it does |
|---------|--------|-------------|
| `/ask [question?]` | 🔵 ASK MODE | Read-only reasoning — analyzes, explains, reviews. Nothing created or saved. Stays active until `/plan` or `/agent` is called. |
| `/plan [task?]` | 🟡 PLAN MODE | Generates artifacts as previews in the conversation. Waits for explicit approval before saving to disk. **Default at session start.** |
| `/agent [task?]` | 🟢 AGENT MODE | Executes autonomously — generates, saves, iterates. Pauses only for 🔴 Critical decisions (security breach, budget exceeded, scope change). |
| `/refine [demand?]` | 🟡 PLAN MODE | Structured demand interview before any work starts. Orchestrator asks up to 5 focused questions (one at a time) to clarify problem, success criteria, constraints, and risks. Outputs a demand brief that feeds Phase 1. |

**Examples:**
```
/ask  Does our current architecture support 10x volume?

/plan Let's design the Silver transformation for the orders table

/agent Run the full pipeline spec phase for this project

/refine We need to centralise customer data from 3 different CRMs
```

---

## Persona commands

Switch to a specific persona without going through the Orchestrator.

| Command | Alias | What it does |
|---------|-------|-------------|
| `/orchestrator` | `/orch` | Routing, Mission Plan, CHANGE MODE |
| `/strategist` | `/strat` | Problem definition, data-product-brief |
| `/architect` | `/arch` | Architecture decisions, stack, ADRs |
| `/finops` | | Cost context, budget review, cost guardrails |
| `/security` | `/sec` | Security assessment, audit, access review |
| `/gov` | `/governance` | Data contracts, governance policy, quality signoff |
| `/planner` | | Backlog, stories, epics, sequencing |
| `/engineer` | `/eng` | Implementation guidance per story, code, runbooks |
| `/analytics` | `/dbt` | dbt models, marts, metrics layer |
| `/ai` | `/ml` | AI/ML Engineer — RAG design, evals, agent architecture, LLM selection, LLMOps, AI observability |
| `/platform` | `/infra` | Data Platform Engineer — IaC (Terraform/Pulumi), Kubernetes for data, environment management, migration planning |

**Examples:**
```
/architect I want to rethink the storage layer. We're hitting query performance issues.

/security Can I give read access to the Gold layer to an external partner?

/dbt The fct_orders model is slow. Can you review it?

/eng I'm starting story HIST-007. What do I need to implement?
```

---

## Workflow commands

| Command | What it does |
|---------|-------------|
| `/change [description]` | Enter CHANGE MODE. Describe what changed and get a targeted impact plan — only the affected personas re-run. |
| `/consult [question]` | Enter CONSULT MODE. Routes to the right expert and answers from your actual project files, not generic knowledge. |
| `/review [artifact name]` | Structured review of an artifact: completeness, gaps, inconsistencies, recommended updates. |

**Examples:**
```
/change We decided to switch from Airflow to Dagster. What needs to be updated?

/consult Why is our Silver pipeline running 3x slower than last month?

/review architecture-document.md
```

---

## Utility commands

| Command | What it does |
|---------|-------------|
| `/scan` | Scans the project for existing SDD artifacts (ADRs, specs, architecture docs, BMAD artifacts). Produces a Discovery Report: what's covered, what's missing, locked decisions, and suggested entry point. Run this first on any existing project. |
| `/status` | Reads `PROJECT-CONTEXT.md` and `.openforge/tasks.md` — shows current mode, phase, artifact statuses, active blockers, and open items. |
| `/tasks` | Reads `.openforge/tasks.md` and displays the task board: in-progress, blocked, resolved this session, and queued. Creates the file from the template if it doesn't exist yet. |
| `/adr [decision]` | Drafts an Architecture Decision Record for the described decision. Asks clarifying questions if needed. |
| `/brainstorm [topic]` | Free, unstructured exploration of a topic. No artifact format, no persona — just thinking. Ends with a ranked shortlist. |
| `/help` | Lists all available commands. |

**Examples:**
```
/status

/adr We need to decide between Iceberg and Delta for our Bronze layer.

/brainstorm How could we make our pipeline more resilient to ERP maintenance windows?
```

---

## Discovery & analysis commands

| Command | What it does |
|---------|-------------|
| `/explain [concept]` | Plain-language explanation of a technical concept, with an analogy. Connects to your project when possible. |
| `/compare [A] vs [B]` | Side-by-side comparison of two tools, patterns, or approaches. Produces a table + recommendation tailored to your project. |
| `/estimate [task]` | Effort, complexity, or cost estimate for a task. Gives a range with explicit assumptions. |
| `/risk [topic]` | Identifies risks related to the topic, each with severity and mitigation. Reads your project files to make it specific. |
| `/recap` | Summarizes what was decided and built in the current session — decisions, artifacts touched, open questions, what's next. |

**Examples:**
```
/explain What is a data contract and why does it matter?

/compare Airflow vs Dagster for a 2-person team on AWS

/estimate Implementing the full Bronze → Silver pipeline for the orders table

/risk Giving an external consultancy direct BigQuery access

/recap
```

---

## Grill commands

Deep interrogation protocols — one question at a time, with a recommended answer after each. Every grill reads project artifacts before asking the first question. Generic questions are a protocol violation.

### Per-persona grills

| Command | What it interrogates |
|---------|---------------------|
| `/grill` | Current persona's domain — routes automatically to the most relevant expert |
| `/grill strategist` | Problem definition, success metrics, stakeholder alignment |
| `/grill architect` | Engine choices, data model grain, ADR completeness |
| `/grill security` | Credential storage, SA hygiene, PII in logs, network isolation |
| `/grill finops` | Cost estimates, budget ceiling, idle resource detection |
| `/grill engineer` | Idempotency, deduplication, schema drift, observability |
| `/grill analytics` | Grain definition, metric consistency, incremental logic |
| `/grill gov` | PII classification, contract completeness, quality rules |
| `/grill planner` | Story granularity, dependency mapping, acceptance criteria |
| `/grill ai` | Eval set, retrieval strategy, hallucination handling, re-embedding plan |

### Thematic grills (cross-persona)

Cut across multiple personas — interrogate a concern, not a role.

| Command | Interrogates |
|---------|-------------|
| `/grill-rag` | RAG systems: retrieval strategy, chunking, embeddings, eval, hallucination, cost |
| `/grill-etl` | ETL pipelines: idempotency, late data, schema evolution, backfill, SLA, retry |
| `/grill-agent` | Multi-agent AI: boundary justification, orchestration, error propagation, cost |
| `/grill-infra` | Infrastructure provisioning: IaC state, environment isolation, compute sizing, CI/CD, drift, DR |
| `/grill-migration` | Platform migrations: dual-write, cutover, validation, rollback, parallel cost |

### Document review mode

| Command | What it does |
|---------|-------------|
| `/grill-docs [artifact]` | Reads the named artifact and interrogates it against the current persona's cross-reference checklist. Surfaces gaps, missing justifications, and contradictions — one finding at a time with a concrete remediation action. |

**Examples:**
```
/grill-docs architecture-document.md

/grill-rag

/grill security

/grill architect ADR-003 feels thin — interrogate it
```

---

## Quick cheat sheet

```
── OPERATING MODES ───────────────────────────────────────
/ask   [question?]          🔵 Read-only reasoning, no files touched
/plan  [task?]              🟡 Generate preview, wait for approval (default)
/agent [task?]              🟢 Execute autonomously, save directly
/refine [demand?]           Structured demand interview before any work

── PERSONAS ──────────────────────────────────────────────
/orchestrator  /orch        Routing & mission planning
/strategist    /strat       Business problem & brief
/architect     /arch        Technical design & ADRs
/finops                     Cost & budget
/security      /sec         Security & access
/gov           /governance  Contracts & governance
/planner                    Backlog & stories
/engineer      /eng         Implementation (per story)
/analytics     /dbt         dbt, marts, metrics
/ai            /ml          RAG, evals, agents, AI observability

── ROUND TABLE ───────────────────────────────────────────
/party-mode [topic]         All personas discuss — synthesis at the end

── GRILL PROTOCOLS ───────────────────────────────────────
/grill [persona?]           Domain-specific interrogation (one Q at a time)
/grill-docs [artifact]      Document cross-reference review
/grill-rag                  RAG system interrogation (cross-persona)
/grill-etl                  ETL pipeline interrogation (cross-persona)
/grill-agent                Multi-agent AI interrogation
/grill-infra                Infrastructure provisioning interrogation
/grill-migration            Platform migration interrogation

── WORKFLOWS ─────────────────────────────────────────────
/change [what changed]      Impact analysis & re-run plan
/consult [question]         Project-aware expert answer
/review [artifact]          Structured artifact review

── STATUS & TRACKING ─────────────────────────────────────
/scan                       Discover existing SDD, lock decisions, find gaps
/status                     Current mode + project state + active blockers
/tasks                      Task board (in-progress, blocked, resolved)
/recap                      Session summary

── UTILITIES ─────────────────────────────────────────────
/adr [decision]             Draft an ADR
/brainstorm [topic]         Free exploration
/help                       This list

── ANALYSIS ──────────────────────────────────────────────
/explain [concept]          Plain-language explanation
/compare [A] vs [B]         Side-by-side comparison
/estimate [task]            Effort / cost / complexity
/risk [topic]               Risk identification
```

---

## `/party-mode` — multi-persona round table

The most powerful command in OpenForge. Brings every relevant persona into the conversation simultaneously, each speaking from their own domain, about the same topic. Use it when a decision has cross-cutting implications and you want all angles before committing.

```
/party-mode [topic or question]
```

**What you get:**

Each relevant persona weighs in with 2-5 sentences — concrete, opinionated, grounded in your actual project artifacts. Followed by a synthesis that surfaces the consensus, the main tension, and a direct recommendation.

**Example output structure:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 PARTY MODE — Should we add Kafka for real-time ingestion?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ DATA ARCHITECT
The current architecture-document.md has ADR-001 documenting that
daily batch was chosen because no use case requires < 1h latency.
Before adding Kafka, that ADR must be revisited. If streaming is
justified, I'd propose Flink over Kafka Streams given our Kubernetes
setup — less operational overhead for a 2-person team.

🗣️ PLATFORM FINOPS ENGINEER
Confluent Cloud starts at ~$200/month — that's 50% of your $400 budget.
Self-hosted Kafka on EKS is cheaper but adds operational burden your
team may not have capacity for. The cost-context.md marks this budget
as a hard cap. This decision needs CTO sign-off before proceeding.

🗣️ SECURITY CONSULTANT
Real-time pipelines expand the attack surface significantly: producers,
consumers, schema registry, and broker all become new entry points.
The current security-assessment.md doesn't cover streaming. If we
proceed, a new architecture review is mandatory before build.

🗣️ DATA ENGINEER
I've worked with Kafka on teams of 2. The operational burden is real:
schema evolution breaks consumers silently, dead letter queues need
monitoring, and on-call coverage for a streaming system is non-trivial.
If the use case is "fresher data", consider 4x daily batch first —
same result, fraction of the complexity.

🗣️ DATA GOV & QUALITY ADVISOR
Every streaming topic is a new data source that needs a contract:
schema, SLA, ownership, and PII treatment. The data-contract-orders.md
would need a streaming variant. Don't build the pipeline before the
contract exists.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Consensus: The current architecture doesn't justify Kafka yet.
Main tension: Manager wants real-time, budget and team size say no.
Blockers: No streaming use case documented, no budget headroom,
          no security assessment for streaming.
Recommendation: Reject Kafka for now. Propose 4x daily batch as
          a low-cost alternative that addresses "fresher data" needs.
          Document as ADR-007.
Next step: /adr Kafka vs increased batch frequency decision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When to use it:**

| Situation | Example |
|-----------|---------|
| Technology choice with trade-offs | `/party-mode Should we use Iceberg or Delta for our Bronze layer?` |
| New requirement that affects multiple phases | `/party-mode The business wants a real-time churn score dashboard` |
| Access or sharing decision | `/party-mode Can we give our data science team direct access to Silver?` |
| Architecture change | `/party-mode We're replacing Airflow with Dagster` |
| Build approach debate | `/party-mode Should we do full load or incremental for the orders table?` |
| Risk assessment before a release | `/party-mode We're going to production next Friday — are we ready?` |

**After the round table**, you can go deeper with any persona:
```
/architect   → continue with the architecture angle
/finops      → dig into the cost analysis
/adr         → draft the decision record immediately
```

---

## How commands interact with the flow

- Commands work **at any point** — they interrupt the current persona and take effect immediately
- After a persona command, you can always type `/orchestrator` to return to routing mode
- `/change` and `/consult` are the two most powerful commands for mid-project work
- `/recap` + `/status` together give you a full picture before ending a session or handing off to another engineer
- Commands are **case-insensitive**: `/ARCHITECT` = `/architect` = `/Architect`

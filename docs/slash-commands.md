# OpenForge Slash Commands

Quick-reference for all `/commands` available in any OpenForge session (Cursor Agent Mode or any LLM that has loaded the `.cursor/rules/openforge.mdc`).

Type a command at the start of your message. It takes effect immediately — no confirmation needed.

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
| `/planner` | `/plan` | Backlog, stories, epics, sequencing |
| `/engineer` | `/eng` | Implementation guidance per story, code, runbooks |
| `/analytics` | `/dbt` | dbt models, marts, metrics layer |

**Examples:**
```
/architect I want to rethink the storage layer. We're hitting query performance issues.

/security Can I give read access to the Gold layer to an external partner?

/dbt The fct_orders model is slow. Can you review it?

/eng I'm starting story HIST-007. What do I need to implement?
```

---

## Mode commands

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
| `/status` | Reads PROJECT-CONTEXT.md and shows current phase, artifact statuses, open items, last session. |
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

## Quick cheat sheet

```
── PERSONAS ──────────────────────────────────────────────
/orchestrator  /orch       Routing & mission planning
/strategist    /strat      Business problem & brief
/architect     /arch       Technical design & ADRs
/finops                    Cost & budget
/security      /sec        Security & access
/gov           /governance Contracts & governance
/planner       /plan       Backlog & stories
/engineer      /eng        Implementation (per story)
/analytics     /dbt        dbt, marts, metrics

── ROUND TABLE ───────────────────────────────────────────
/party-mode [topic]         All personas discuss — synthesis at the end

── MODES ─────────────────────────────────────────────────
/change [what changed]      Impact analysis & re-run plan
/consult [question]         Project-aware expert answer
/review [artifact]          Structured artifact review

── UTILITIES ─────────────────────────────────────────────
/scan                       Discover existing SDD, lock decisions, find gaps
/status                     Current project state
/adr [decision]             Draft an ADR
/brainstorm [topic]         Free exploration
/help                       This list

── ANALYSIS ──────────────────────────────────────────────
/explain [concept]          Plain-language explanation
/compare [A] vs [B]         Side-by-side comparison
/estimate [task]            Effort / cost / complexity
/risk [topic]               Risk identification
/recap                      Session summary
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

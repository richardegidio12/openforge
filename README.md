<div align="center">

<img src="docs/assets/logo.svg" alt="OpenForge" width="480"/>

<br/>

**The AI-driven method for data engineering teams that build things that last.**

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red)](https://github.com/your-username/openforge)

</div>

---

## What is OpenForge?

**OpenForge is an open-source AI method for building data platforms** — from the first business conversation all the way to production pipelines with governance, security, and quality in place.

It works by giving you a set of **specialized AI personas**, each one an expert in a different phase of data engineering. You talk to them one at a time. They ask the right questions, make the right decisions, and generate the documents your project needs — consuming what the previous persona produced and feeding what the next one will need.

**You don't need to be a data engineer to start. You don't need to install anything. You need an LLM and a problem worth solving.**

> Think of it as a data engineering team in a box — available at any hour, with no onboarding time.

---

## The problem it solves

Small and mid-size data teams fail not from lack of technology, but from lack of **structured thinking**:

- They build the right pipeline for the wrong problem
- They create tables nobody trusts because nobody documented what a row means
- They discover PII issues only after exposing the data
- They ship pipelines that work on day 1 and silently break on day 47
- They can't answer "what changed and why?" when a number is wrong
- Every engineer on the team has a different mental model of the same system

OpenForge solves this by making **structured thinking the default**, not the exception.

---

## How it works in 60 seconds

```
You have a problem worth solving
         │
         ▼
┌─────────────────┐
│  Orchestrator   │  ← Start here. Always. Describe your project.
│  (AI persona)   │  It diagnoses where you are and tells you exactly
└────────┬────────┘  what to do next.
         │
         ▼
┌─────────────────┐
│  The right      │  ← Each persona is an expert: Strategist, Architect,
│  persona for    │    Security Consultant, Data Engineer, Analytics Engineer...
│  each phase     │    They interview you, make decisions, generate documents.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Artifact saved │  ← Every conversation ends with a document:
│  to your project│    a brief, an architecture, a data contract,
└────────┬────────┘    a pipeline spec, a security assessment...
         │
         ▼
┌─────────────────┐
│  Next persona   │  ← The next expert reads what the previous one produced.
│  picks up where │    No context lost. No repeated explanations.
│  the last left  │    The project advances.
└─────────────────┘
```

**In Cursor Agent Mode**, all of this happens in a single conversation. The agent switches personas internally, saves files to your project automatically, and reads them before each new phase. You just answer questions.

---

## What makes OpenForge different

<table>
<tr>
<td width="50%">

### Without OpenForge
- Engineer starts coding without a clear problem statement
- Architecture chosen based on what the team already knows, not what the problem needs
- Data contracts don't exist until something breaks
- "Who owns this dataset?" → nobody knows
- PII found in production 3 months after launch
- Pipeline fails silently at 2am, nobody notices until the commercial meeting
- New engineer joins and spends 2 weeks understanding the system

</td>
<td width="50%">

### With OpenForge
- Every project starts with a validated problem statement
- Architecture decisions are documented with explicit trade-offs
- Data contracts exist before the first line of code
- Every dataset has a named owner
- PII is identified and handled in Phase 3, not Phase ∞
- Every pipeline has an alert, a runbook, and a freshness SLO
- New engineer reads the artifacts and is productive in a day

</td>
</tr>
</table>

---

## The personas

OpenForge has **9 specialized personas**, each covering a specific phase of the data project lifecycle.

| # | Persona | What they do | When to use |
|---|---------|-------------|-------------|
| 00 | **Orchestrator** | Diagnoses your project and delivers a precise Mission Plan | Always first — and whenever something changes |
| 01 | **Data Product Strategist** | Turns a business problem into a structured brief | Before any technical decision |
| 02 | **Data Architect** | Designs the simplest architecture that solves the problem | After the brief is approved |
| 03 | **Data Gov & Quality Advisor** | Defines data contracts, ownership, PII rules, quality SLAs | Before build AND after build |
| 04 | **Pipeline Planner** | Breaks the project into concrete, sequenced engineering stories | After architecture and contracts |
| 05 | **Data Engineer** | Implements ingestion, Bronze, Silver layers with production-grade patterns | During build, per story |
| 06 | **Analytics Engineer** | Builds Gold layer dbt models that analysts can actually trust | During build, per story |
| 07 | **Platform FinOps Engineer** | Makes cost constraints visible before they become surprises | Transversal — any time |
| 08 | **Security Consultant** | Identifies security gaps before they become incidents | After architecture, before production |

---

## Skills

Every technical persona applies a set of **cross-cutting skills** — principles that ensure the output is not just technically correct, but humanly maintainable.

> "A LLM can hold 10x more complexity than a human engineer can maintain. OpenForge is designed to close that gap."

| Skill | What it enforces |
|-------|-----------------|
| **Software Engineering** | Boring over clever. Names that explain intent. One function, one responsibility. Tests that teach business rules. Scale for 10x, not 100x. |
| **Observability** | Structured logs, freshness SLOs, volume alerts, Grafana dashboards, runbooks. Nothing ships without a way to know it's broken. |
| **Testing Strategy** | Unit tests for logic, dbt contract tests for quality, integration tests for pipelines, reconciliation tests for correctness. |
| **Incident Response** | SEV classification, 5-step protocol, post-mortems within 48h. Because 2am failures are inevitable — how you handle them is a choice. |
| **Data Modeling** | Grain-first design, dimensional modeling, one metric one definition, no PII in Gold, SCD patterns, naming conventions. |
| **Modern Data Stack** | Iceberg vs Delta vs Hudi, Trino, Spark, Flink, Apache Ranger, Kubernetes deployment patterns for data workloads. |

---

## MCP Integrations

When used in Cursor Agent Mode, OpenForge can **connect directly to your infrastructure** via MCPs — running queries, checking pipeline status, reading logs, creating issues, all without leaving the conversation.

| Group | Systems |
|-------|---------|
| Code & Communication | GitHub, Slack |
| Data Warehouse & Query | BigQuery, PostgreSQL, Trino, Apache Hive |
| Orchestration | Dagster, Apache Airflow, Apache Flink |
| Observability | Grafana, Prometheus, ELK Stack, Thanos |
| Cloud Infrastructure | Kubernetes (EKS / AKS / GKE), Apache Ranger |

**The difference MCPs make:**

Without MCPs → *"Here's how to run this query to check the issue..."*
With MCPs → *"I ran the query. The reconciliation divergence is 2.3% — above the 0.5% SLO. Here's the breakdown by order status..."*

→ See [`mcp/`](mcp/) for setup instructions.

---

## Using OpenForge

### Option 1 — With any LLM (manual mode)

No setup. Works with Claude, ChatGPT, Gemini, or any LLM.

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/openforge.git
   ```
2. Open a persona file in `personas/`
3. Copy the **Activation Prompt** at the bottom
4. Paste into a new LLM chat, add your context, start the conversation
5. Save the generated artifact to your project folder
6. Move to the next persona

**Full guide:** [`HOW-TO-USE.md`](HOW-TO-USE.md)

---

### Option 2 — With Cursor Agent (recommended)

One conversation. Multiple personas. Artifacts saved automatically. The agent reads existing files before each new phase — no copy-pasting context.

**Setup (one time):**
```bash
# In your project folder:
git clone https://github.com/your-username/openforge.git openforge
mkdir -p .cursor/rules
cp openforge/.cursor/rules/openforge.mdc .cursor/rules/
```

Open your project in Cursor Agent mode (⌘⇧I) and say:

```
I want to build a [describe your project]. Guide me.
```

The agent starts as the Orchestrator, transitions through the right personas, saves every artifact, and is ready for your next question.

At any point in the conversation, use **slash commands** to call a specific persona or mode directly:

```
/architect        → switch to Data Architect
/change           → trigger CHANGE MODE (impact analysis)
/brainstorm       → free exploration, no structure
/risk             → identify risks in the current topic
/status           → show project state from PROJECT-CONTEXT.md
/party-mode       → round table: all personas discuss the same topic,
                    each from their domain, ending with a synthesis
```

**Full guide:** [`docs/cursor-agent-mode.md`](docs/cursor-agent-mode.md) · **Slash commands:** [`docs/slash-commands.md`](docs/slash-commands.md)

---

### Option 3 — As a project-aware consultant

Clone OpenForge **inside an existing project** and use it as an AI consultant that knows your specific codebase:

```bash
cd ~/your-existing-project
git clone https://github.com/your-username/openforge.git openforge
mkdir -p .cursor/rules
cp openforge/.cursor/rules/openforge.mdc .cursor/rules/
```

Then ask things like:

- *"My pipeline failed last night — can you check what happened?"*
- *"Does our architecture support 10x current volume?"*
- *"Can I give the external consultant access to this dataset?"*
- *"Our GCP bill went up 40% — what's causing it?"*

The agent reads your actual code, queries your infrastructure (with MCPs), and answers with specifics — not generic advice.

**Full guide:** [`docs/consulting-mode.md`](docs/consulting-mode.md)

---

## Project structure

```
openforge/
│
├── personas/          ← The 9 AI personas with full instructions + activation prompts
├── skills/            ← Cross-cutting skills applied by technical personas
├── templates/         ← Ready-to-use templates for every artifact
│   └── project-context.md  ← Session compaction artifact (resume any project in seconds)
├── examples/          ← Complete worked example: e-commerce analytics project
├── workflows/         ← Full project flow documentation
├── mcp/               ← MCP integration guides and config template
├── docs/              ← Cursor agent mode, consulting mode guides
│   └── decisions/     ← ADRs for OpenForge's own design decisions
│
├── .cursor/rules/     ← openforge.mdc — the Cursor Agent rule (auto-activates)
├── SPEC.md            ← Framework specification (source of truth for contributions)
├── HOW-TO-USE.md      ← Step-by-step guide for each phase
├── CONTRIBUTING.md    ← How to contribute
└── LICENSE            ← MIT
```

### The session memory artifact

Every project folder gets a `PROJECT-CONTEXT.md` — a compact (~100 lines) snapshot of the project's current state. It lets any agent or engineer pick up exactly where the last session ended:

```
Resuming from PROJECT-CONTEXT.md
Phase 4 — Pipeline Planning  ·  Next: activate Pipeline Planner
3 of 9 artifacts ready  ·  1 open blocker  ·  Last session: 2 days ago
```

It's updated automatically in Cursor Agent Mode, and can be updated manually in a single prompt in any other LLM.

---

## Principles

1. **Problem before technology** — no architectural decisions before the brief is approved
2. **Simplicity first** — the simplest solution a human can maintain beats the most elegant one nobody understands
3. **Contracts before build** — quality is defined before coding, not discovered after
4. **Raw data is sacred** — Bronze is never modified
5. **Done = tested + documented + monitored** — "works on my machine" doesn't exist in data
6. **Governance nobody follows is worse than no governance** — calibrate rigor to team size
7. **Recommendations must be traceable** — every technical choice follows a decision tree, is scored against project anchors, and states the conditions that would reverse it. See [`docs/decision-framework.md`](docs/decision-framework.md)

---

## Contributing

OpenForge is open source and actively welcoming contributions.

**You can contribute:**
- 🎭 **Persona improvements** — sharper questions, clearer principles, better warning signals
- 🛠️ **New skills** — patterns for specific domains or technical areas
- 🔌 **New MCP integrations** — connect OpenForge to more tools
- 📋 **New templates** — alternative formats for specific contexts
- 🌍 **Examples** — other domains: healthcare, fintech, SaaS, logistics
- 🌐 **Translations** — the method in other languages
- 🐛 **Fixes** — inconsistencies, broken links, outdated content

**How to start:**
1. Open an [issue](https://github.com/your-username/openforge/issues) describing what you want to change
2. Fork → branch → PR
3. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for conventions

> No contribution is too small. A clearer question in a persona, a better example query, a fixed typo — all of it makes OpenForge better for everyone.

---

## License

MIT — free to use, modify, and distribute. See [`LICENSE`](LICENSE).

---

<div align="center">

Built by data engineers, for data engineers — and for everyone who works with them.

**[Get started →](HOW-TO-USE.md)** · **[See an example →](examples/ecommerce-analytics/)** · **[Contribute →](CONTRIBUTING.md)**

</div>

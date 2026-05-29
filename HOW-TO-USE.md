# How to Use OpenForge

---

## The recommended experience: Cursor Agent Mode

You don't open persona files. You don't copy prompts. You just talk.

**One-time setup:**
```bash
# Inside your project folder
git clone https://github.com/richardegidio12/openforge.git openforge
mkdir -p .cursor/rules
cp openforge/.cursor/rules/openforge.mdc .cursor/rules/
```

Open Cursor, switch to Agent Mode (`⌘⇧I`), and start:

```
I want to build a data pipeline that consolidates sales data from 3 sources
into a single dashboard. Where do I start?
```

That's it. The agent diagnoses your project, routes to the right persona, asks the questions, generates the artifacts, and saves everything to your project folder — all in the same conversation.

---

## Using with Claude Code (VS Code or terminal)

Claude Code reads a `CLAUDE.md` file at the project root automatically — it becomes part of every session's instructions without any copy-pasting.

**One-time setup:**
```bash
# Inside your project folder
git clone https://github.com/richardegidio12/openforge.git openforge
cp openforge/CLAUDE.md ./CLAUDE.md
```

Open Claude Code in VS Code (`⌘⇧P → "Claude Code"`) or in the terminal:
```bash
claude
```

Start talking:
```
I want to build a data pipeline that consolidates sales data from 3 sources.
Where do I start?
```

The experience is identical to Cursor Agent Mode — same personas, same slash commands, same modes, same artifact saves. Claude Code reads and writes your project files directly.

**The one difference from Cursor:** `CLAUDE.md` is a project file committed to your repository. If you update OpenForge, refresh it:
```bash
cp openforge/CLAUDE.md ./CLAUDE.md
```

### CLAUDE.md hierarchy (how Claude Code loads context)

Claude Code reads `CLAUDE.md` files from the current directory up to the home directory — useful for multi-project setups:

| File | When it loads | What to put there |
|------|--------------|-------------------|
| `~/.claude/CLAUDE.md` | Every session, globally | Your personal preferences, team conventions |
| `my-project/CLAUDE.md` | When working in this project | OpenForge instructions (copy from `openforge/CLAUDE.md`) |
| `my-project/src/CLAUDE.md` | When working inside `src/` | Component-specific context |

> **Tip:** If you work on multiple data projects, put OpenForge in `~/.claude/CLAUDE.md` once — it activates for every project automatically.

---

## Three modes of operation

OpenForge operates in three explicit modes. You control which one you're in.

### 🔵 Ask Mode — explore and understand
```
/ask  Is our current architecture ready for 10x volume?
/ask  What is the difference between SCD Type 1 and Type 2?
/ask  Why is the Silver pipeline running slow?
```
The agent reads your project files and answers with specifics. Nothing is created or modified.

### 🟡 Plan Mode — generate and review (default)
The default mode when you start a session. The agent generates artifacts, shows them in the conversation, and waits for your approval before saving anything to disk.

```
/plan  Let's design the architecture for the orders pipeline
```

After generating: `🟡 Ready to save → architecture-document.md. Proceed?`

You review, approve, request changes — your choice.

### 🟢 Agent Mode — execute autonomously
```
/agent  Run the full pipeline planning phase for this project
```
The agent executes: generates, saves, advances. It pauses only when a decision genuinely requires you — budget exceeded, security-critical finding, scope change. Everything else it resolves internally and logs.

---

## Starting a new project

The Orchestrator always goes first. It diagnoses where you are and tells you exactly what to do next.

```
I want to build [describe your project]. Help me start.
```

Or if you prefer to be more structured:

```
/refine  We need to centralise customer data from Salesforce, our ERP, and a CSV export
```

`/refine` runs a structured interview (max 5 questions, one at a time) before any technical work starts — problem, success criteria, constraints, risks. It generates a demand brief that feeds every subsequent phase.

---

## A realistic session

Here's what a typical session actually looks like:

```
You:    I want to build a pipeline that pulls orders from our ERP into BigQuery
        for the finance team. Budget is around $300/month.

Agent:  [reads project files]
        🟡 PLAN MODE
        I'll start as the Orchestrator. A few questions...
        [asks 3-4 diagnostic questions]
        Here's your Mission Plan: [phases, order, estimated time]
        Shall I proceed to Phase 1 — Data Product Strategist?

You:    Go

Agent:  [switches to Strategist, asks questions about the business problem]
        Here's the data-product-brief.md: [full artifact]
        🟡 Ready to save → data-product-brief.md. Proceed?

You:    Looks good. Save it.

Agent:  ✅ Saved → data-product-brief.md
        📋 Carrying forward: finance reporting use case, D-1 latency, 2 consumers
        Shall I proceed to Phase 2 — Data Architect?

You:    Yes, but first — is BigQuery the right choice at this budget?

Agent:  [switches to Ask Mode implicitly, reads cost-context]
        🔵 At your $300/month budget and estimated 5TB/month query volume,
        BigQuery on-demand would cost ~$31/month. That's well within budget.
        The concern would be at 50TB+/month — worth documenting as a scaling note.
        Want me to continue with architecture?

You:    Yes, go — and use /agent from here

Agent:  🟢 AGENT MODE
        [runs through Architecture, FinOps, Security in parallel]
        [saves artifacts, logs resolutions, surfaces only real blockers]
```

---

## Mid-project commands

Once a project is underway, these are the most useful commands:

| What you want | Command |
|--------------|---------|
| Understand something without changing anything | `/ask [question]` |
| Review an artifact before proceeding | `/review architecture-document.md` |
| Something changed — update the plan | `/change We switched from Airflow to Dagster` |
| Ask a domain expert directly | `/security` `/finops` `/architect` `/ai` |
| Get all perspectives on a hard decision | `/party-mode Should we use Iceberg or Delta?` |
| Deep interrogation of a design | `/grill` `/grill-rag` `/grill-etl` |
| Check project state | `/status` |
| Check what's blocked or in progress | `/tasks` |
| Summarize before ending the session | `/recap` |

---

## Working with personas

You never need to open a persona file. Each persona is activated by the agent when needed — or directly by you with a slash command.

| Persona | Slash command | When to call directly |
|---------|-------------|----------------------|
| Orchestrator | `/orchestrator` | Routing, mission plan, scope change |
| Data Product Strategist | `/strategist` | Problem definition, brief |
| Data Architect | `/architect` | Architecture, stack decisions, ADRs |
| Platform FinOps Engineer | `/finops` | Cost review, budget check |
| Security Consultant | `/security` | Security assessment, access decisions |
| Data Gov & Quality Advisor | `/gov` | Data contracts, PII, quality rules |
| Pipeline Planner | `/planner` | Backlog, stories, epics |
| Data Engineer | `/engineer` | Implementation guidance per story |
| Analytics Engineer | `/analytics` or `/dbt` | dbt models, marts, metrics |
| AI/ML Engineer | `/ai` | RAG design, evals, agent architecture |

**You don't need to follow the phase sequence.** Call any persona at any time. The Orchestrator routes intelligently.

---

## Resuming a session

The agent creates and updates `PROJECT-CONTEXT.md` automatically. When you return:

```
[open Cursor Agent Mode, or paste PROJECT-CONTEXT.md into any LLM]
Continue from where we left off.
```

The agent reads the context file and picks up exactly where you ended — phase, artifacts, open items, last decision made.

```
📋 Resuming — Orders Analytics Project
🟡 PLAN MODE
Phase 4 — Pipeline Planning  ·  Next: activate Pipeline Planner
⏸️ Blocked: 1 item (waiting on data contract for ERP source)
🔄 In progress: architecture-document.md (draft, pending approval)
```

---

## Project folder after a full run

```
my-project/
├── PROJECT-CONTEXT.md           ← session memory (auto-updated)
├── .openforge/tasks.md          ← task board (auto-updated in Agent Mode)
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

## Common scenarios

| Scenario | What to do |
|----------|-----------|
| New project from scratch | Start with Orchestrator or `/refine` |
| Joining an existing project | `/scan` — maps existing artifacts, locks prior decisions |
| Something changed mid-project | `/change [what changed]` — targeted impact plan |
| Hard architectural decision | `/party-mode [question]` — all personas weigh in |
| Validating before production | `/party-mode Are we production-ready?` |
| Understanding an unfamiliar concept | `/ask [concept]` or `/explain [concept]` |
| Quick POC | `/agent Run phases 1 and 2 quickly, skip governance` |

---

## Using with any LLM (without Cursor)

If you're using ChatGPT, Claude.ai, Gemini, or another LLM without Cursor:

1. Open [`personas/00-orchestrator.md`](personas/00-orchestrator.md)
2. Copy the **Activation Prompt** at the bottom of the file
3. Paste into a new conversation, describe your project
4. Save the output artifact to your project folder
5. For each subsequent phase: copy the relevant persona's Activation Prompt, add the output of the previous phase as context

**To resume a session:** paste `PROJECT-CONTEXT.md` before the activation prompt.

> The Cursor Agent Mode experience is significantly better — all persona transitions, artifact saves, and context passing happen automatically. Manual mode works, but expect more copy-pasting.

---

**Full slash command reference:** [`docs/slash-commands.md`](docs/slash-commands.md)

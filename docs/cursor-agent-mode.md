# OpenForge in Cursor — Agent Mode

How to use OpenForge as a single, fluid session in Cursor, with automatic persona transitions and artifacts generated and fed back into the conversation.

---

## Setup (once per machine)

1. Clone OpenForge somewhere fixed on your machine:
   ```bash
   git clone https://github.com/richardegidio12/openforge.git ~/openforge
   ```

2. Create your project folder:
   ```bash
   mkdir ~/projects/my-project
   ```

3. In Cursor, open both as a workspace:
   - `File → Add Folder to Workspace → ~/openforge`
   - `File → Add Folder to Workspace → ~/projects/my-project`

The `.cursor/rules/openforge.mdc` file from the repository is automatically detected by Cursor and activates agent mode for the entire session.

---

## How to start

Open **Cursor Agent** (⌘⇧I) — not the simple Chat.

> The Agent has access to file tools: it reads and writes files in your project automatically, without you having to copy and paste.

Just type:

```
I want to start a data project. Can you guide me?
```

or, if you already have context:

```
I want to build a churn analytics pipeline for the Customer Success team.
We have a PostgreSQL database with usage events and want to predict cancellations
30 days in advance. Team of 2, budget ~$400/month.
```

---

## What a real session looks like

Below is a real conversation between the user and the OpenForge Agent in Cursor.

---

**User:**
> I want to build a churn analytics pipeline. Can you start?

---

**OpenForge Agent:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 ORCHESTRATOR — Entry Point
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

To map the best path, tell me: which of these documents do you already have?

- [ ] `data-product-brief.md`
- [ ] `architecture-document.md`
- [ ] `cost-context.md`
- [ ] `data-contract-[name].md`
- [ ] `governance-policy.md`
- [ ] `pipeline-spec.md`
- [ ] `quality-signoff.md`

If none, just say **"none"**.

---

**User:**
> none

---

**OpenForge Agent:**

New project. 3 more questions:

1. Describe the project in 2-3 sentences: what do you want to build and for whom?
2. What's the team size? (e.g. just me, 2-3 people, data squad)
3. Is there a defined monthly infrastructure budget?

---

**User:**
> Pipeline that processes usage events from our SaaS and identifies customers at churn risk.
> Output: Gold table with a risk score per customer, updated daily.
> Consumers: CS team in Salesforce and an internal dashboard.
> Team: 2 engineers. Budget: ~$400/month.

---

**OpenForge Agent:**

## 🗺️ Mission Plan — Churn Analytics

**Current state:** New project, no artifacts. Budget defined ($400/month).
**Mode:** Full Project

### Next step (NOW)
**Persona:** Platform FinOps Engineer (Context Mode)
**Why:** Budget was mentioned but not documented. With SaaS event volume and Salesforce integration, costs can vary significantly. Documenting the financial context before architecture prevents decisions that will need to be reversed.

### Estimated sequence
| Order | Persona | Estimate | Prerequisite |
|-------|---------|----------|-------------|
| 1 | FinOps Engineer | 20 min | — |
| 2 | Data Product Strategist | 45 min | cost-context |
| 3 | Data Architect | 60 min | brief |
| 4 | Security Consultant | 30 min | architecture |
| 5 | Gov & Quality (Contract) | 45 min | brief + architecture |
| 6 | Pipeline Planner | 60 min | all above |
| 7 | Data Engineer + Analytics Eng. | per story | pipeline-spec |
| 8 | Gov & Quality (Validation) | 30 min | build complete |
| 9 | Security (Pre-prod Audit) | 30 min | build complete |

### ⚠️ Identified risks
- Salesforce integration may require a paid API — verify before architecture
- Churn score likely requires a feature store or ML layer — clarify in the brief whether it's a model or a heuristic rule

✅ Shall I proceed to **Phase 2.5** with the **Platform FinOps Engineer**?

---

**User:**
> yes

---

**OpenForge Agent:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 PLATFORM FINOPS ENGINEER — Phase 2.5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

📂 Reading: no artifacts yet.

Great. I need to understand the financial context before any technical decision. I'll ask at most 6 questions.

**1/6 — Budget:** You mentioned ~$400/month. Is this a hard cap or an estimate that can be adjusted with approval?

---

**User:**
> Hard cap. Anything above requires CTO approval.

---

**OpenForge Agent:**

**2/6 — Current cloud:** Do you already use a cloud provider? Are there existing commitments (contracts, credits, reserved instances)?

---

**User:**
> AWS. We have $200 in monthly credits remaining for 6 more months (startup program).

---

**OpenForge Agent:**

**3/6 — Volume:** Estimated event volume: how many events/day? How many active customers?

---

**User:**
> ~500k events/day. ~8,000 active customers.

---

**OpenForge Agent:**

**4/6 — Salesforce:** Is the Salesforce integration push (you write to Salesforce) or pull (Salesforce reads from you)? Does Salesforce have an API cost?

---

**User:**
> Push. We update a custom field in Salesforce via API. We already pay for Salesforce;
> there's no additional API cost in the current plan.

---

**OpenForge Agent:**

**5/6 — Existing tools:** Do you already pay for any data tools? (e.g. dbt Cloud, Databricks, Snowflake, Fivetran, any BI tool)

---

**User:**
> We have Metabase self-hosted on EC2. Nothing else.

---

**OpenForge Agent:**

**6/6 — Priority:** If there's a conflict between cost and an important technical feature, what's the priority — stay within budget or deliver the feature?

---

**User:**
> Stay within budget. We can deliver the feature in phases if needed.

---

**OpenForge Agent:**

Understood. Generating the artifact.

````markdown
# Cost Context
**Project:** Churn Analytics
**Date:** [today]
**Restriction Level:** 🟡 Moderate

## Financial Context
| | |
|--|--|
| Monthly budget | $400 USD (hard cap — CTO approval required above) |
| Cloud | AWS — $200/month in credits (6 months remaining) |
| Effective budget for the next 6 months | ~$600/month (budget + credits) |
| Salesforce API | No additional cost |
| Metabase | Self-hosted on EC2 (already running) |

## Cost Guardrails
1. S3 + Athena preferred over Redshift — Redshift ($180+/month) consumes >45% of budget alone
2. No heavy managed services in MVP (e.g. Glue, EMR) — Lambda/Fargate for light transformations
3. AWS credits prioritized for compute — not storage
4. Mandatory re-evaluation when AWS credits expire (month 7)
5. Salesforce push: max 1x/day to avoid rate limiting and complexity

## Review Triggers
- AWS bill > $300/month → Revision Mode
- Event volume grows to 2M+/day → Revision Mode
- AWS credits run out → Revision Mode urgent
````

✅ Saved → `cost-context.md`

📋 Carrying forward:
- Hard budget of $400/month — avoid Redshift, EMR, Glue
- AWS credits of $200/month for 6 months — window to experiment without real cost
- Volume: 500k events/day, 8k customers — daily batch viable, no streaming needed
- Salesforce: daily push via API — no additional cost

✅ Shall I proceed to **Phase 1** with the **Data Product Strategist**?

---

**User:**
> yes

---

**OpenForge Agent:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 DATA PRODUCT STRATEGIST — Phase 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

📂 Reading: `cost-context.md` ✓

I know the budget is constrained and the volume doesn't require streaming. Now I need to understand the **business problem** before any technical decision.

**Block 1 — Problem**

You mentioned "identifying customers at churn risk". I'd like to understand better:

- Does the CS team **already know** which customers are at risk today? How do they find out?
- When a customer cancels, is there a behavior pattern you've already observed (e.g. stopped using feature X, reduced logins)?
- What's the cost of a cancellation? (average contract value, LTV)

---

*(the conversation continues — Strategist runs blocks 2 and 3, generates the brief, saves it, and asks if it can proceed to the Architect)*

---

## What happens behind the scenes

While you're talking, the Cursor Agent is:

```
churn-analytics/
├── cost-context.md          ← generated and saved by FinOps (Phase 2.5)
├── data-product-brief.md    ← will be generated by Strategist (Phase 1)
├── architecture-document.md ← will be generated by Architect (Phase 2)
├── ...
```

Each persona reads the already-existing files before starting. You never need to copy and paste context between phases. The conversation flows as a single session with a single interlocutor who changes hats.

---

## Usage tips

**To pause and resume:**
```
pause — I'll continue later
```
The Agent confirms where it stopped. In the next session, open the Cursor Agent and say:
```
I want to continue the churn analytics project. Can you check what has already been generated?
```
The Agent reads the existing files and resumes from where it left off.

**To change something mid-project:**
```
changed my mind: we want to use Snowflake instead of Athena
```
The Agent enters CHANGE MODE automatically, assesses the impact and re-runs only the affected personas.

**To focus on a specific phase:**
```
I want to review only the architecture. Can you activate the Data Architect?
```

**For the build phase (per story):**
```
I'm on story HIST-004. Can you activate the Data Engineer?
```
The Agent reads `pipeline-spec.md` and `data-contract.md` and guides the story implementation.

---

## Why it works

The `.cursor/rules/openforge.mdc` is in the OpenForge repository. When you add OpenForge as a workspace folder in Cursor, this rule activates automatically for every session. You don't need to copy any prompt — the Agent already knows the method.

Cursor Agent mode has access to file tools, so it generates and saves artifacts directly in your project. Feedback between personas happens via file reading — exactly what the method was designed to do.

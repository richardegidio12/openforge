# OpenForge Decision Framework

How OpenForge produces consistent, traceable, non-contradictory recommendations — regardless of who runs the session or which LLM is used.

---

## The four determinism mechanisms

### 1. Decision Anchors — constrain the solution space early

Six project parameters, captured in `PROJECT-CONTEXT.md` after Phase 1, that act as **hard constraints** on every subsequent recommendation. The agent applies them as filters before suggesting anything.

| Anchor | Why it matters |
|--------|---------------|
| **Team size** | A tool that's excellent for a 10-person team may be operationally unsustainable for 2 people. Team size caps complexity. |
| **Budget** | Hard cap. No recommendation may exceed 30% of the stated budget without an explicit flag and justification. |
| **Cloud** | Constrains managed service choices. A GCP project shouldn't be recommended Redshift. |
| **PII present** | Binary. If yes → security and governance phases are mandatory, not optional. |
| **Target environment** | POC = reduce ceremony. Production = full rigor. This single anchor changes the expected depth of every artifact. |
| **Latency requirement** | If D-1 batch is sufficient, streaming is never recommended as the primary solution — regardless of how technically interesting it is. |

**How to use them:**
1. The Orchestrator or FinOps Engineer fills the anchors in Phase 1–2
2. They're stored in the `Decision Anchors` section of `PROJECT-CONTEXT.md`
3. Every persona reads them at the start of its session
4. Any recommendation that would violate an anchor must be explicitly flagged as an exception

---

### 2. Decision Trees — deterministic logic for common choices

For the most frequent technology decisions in data engineering, OpenForge uses explicit `if/then` trees instead of open-ended exploration. The same inputs always produce the same output.

#### Table format

```
Multi-engine queries required?
  └─ Yes → Iceberg
  └─ No → Databricks/Delta Live Tables primary?
            └─ Yes → Delta
            └─ No → CDC upserts > 10k/min?
                      └─ Yes → Hudi
                      └─ No → Iceberg (default)
```

#### Orchestration

```
Existing Airflow investment OR DAG-heavy large team?
  └─ Yes → Airflow
  └─ No → Kubernetes-native AND event-driven?
            └─ Yes → Dagster (k8s executor)
            └─ No → Dagster (default for teams ≤ 8)
```

#### Query engine

```
GCP-native AND no multi-engine requirement?
  └─ Yes → BigQuery
  └─ No → Multi-catalog federation needed (Iceberg + Hive + Delta)?
            └─ Yes → Trino
            └─ No → AWS-native AND serverless preference?
                      └─ Yes → Athena
                      └─ No → Spark SQL
```

#### Streaming (only evaluate if latency anchor ≠ Batch)

```
Stateful processing + complex event patterns?
  └─ Yes → Flink
  └─ No → Simple filtering/routing in Kafka ecosystem?
            └─ Yes → Kafka Streams
            └─ No (managed, AWS) → Kinesis
```

#### SCD type (slowly changing dimensions)

```
History of changes required by a use case?
  └─ No → SCD Type 1 (overwrite — default)
  └─ Yes → Need point-in-time reconstruction?
              └─ Yes → SCD Type 2 (versioned rows)
              └─ No → SCD Type 3 (current + previous column)
```

---

### 3. Scored Rubrics — traceable comparisons

Every `/compare` and `/party-mode` produces a scored table before the recommendation. Five fixed dimensions, scored 1–5, weighted by project context.

```
| Dimension          | Option A | Option B |
|--------------------|----------|----------|
| Operational burden | X/5      | X/5      |
| Cost fit           | X/5      | X/5      |
| Team skill fit     | X/5      | X/5      |
| Scalability        | X/5      | X/5      |
| Ecosystem fit      | X/5      | X/5      |
| Total              | X/25     | X/25     |
```

**Scoring guidelines:**

| Dimension | 1 (poor) | 5 (excellent) |
|-----------|----------|---------------|
| Operational burden | Requires dedicated ops engineer | Zero-ops, fully managed |
| Cost fit | Exceeds budget or 50%+ of budget | < 10% of budget |
| Team skill fit | Steep learning curve, no prior experience | Team already uses it |
| Scalability | Hits ceiling within 1 year at current growth | Handles 100x current load |
| Ecosystem fit | Requires new tooling to integrate | Native integration with current stack |

After the table:
> "This recommendation holds if: [conditions]. It reverses if: [conditions]."

This makes recommendations auditable — you can see the exact reasoning and what would change it.

---

### 4. Contradiction Detection — immutable decisions

Once a decision is recorded in `Key Decisions` (PROJECT-CONTEXT.md) or in an approved artifact, it is **locked**. The agent will not contradict it silently.

**What triggers a contradiction check:**
- Any recommendation that touches a technology already chosen
- Any recommendation that touches a pattern already documented in an ADR
- Any scope change that conflicts with the data-product-brief

**What happens when a contradiction is detected:**
```
⚠️ CONTRADICTION DETECTED
Previous decision: 2024-04-10 — Use Iceberg over Delta
  (source: architecture-document.md ADR-001)
Current recommendation would change this.

Options:
A) Keep the previous decision — reason it still holds
B) Override it — triggers /change to update affected artifacts
C) Clarify scope — the decisions may not actually conflict
```

The user chooses. The agent never overwrites silently.

---

## Recommendation signature

Every technical recommendation ends with a **recommendation signature** — a compact block that makes the reasoning auditable:

```
📌 Recommendation: [what was recommended]

Based on:
- Team size: 2 engineers (anchor)
- Budget: 🔴 Tight — $400/month (anchor)
- Latency: Batch D-1 (anchor)
- Existing stack: GCP + dbt (from architecture-document.md)

Holds if: team stays ≤ 3, budget stays constrained, no streaming use case emerges
Reverses if: budget increases to $800+/month OR real-time use case documented in brief
```

This signature is the difference between "the AI said so" and "the AI said so because of these specific conditions, and here's what would change it."

---

## The consistency guarantee

Two engineers running the same OpenForge session for the same project, with the same Decision Anchors, will reach the same technology recommendations — because the recommendations follow deterministic trees, not open-ended exploration.

What can still differ between sessions:
- The exact wording of artifacts (LLMs are non-deterministic in text generation)
- The questions asked during an interview (some variation is expected)
- The depth of analysis in edge cases

What will NOT differ:
- The technology choice for any decision covered by a decision tree
- The recommendation direction when scored rubrics are applied
- The detection of contradictions with prior decisions

---

## When to override the decision trees

Decision trees are defaults, not rules. A team may have valid reasons to deviate. The protocol for overriding:

1. Acknowledge the default recommendation: *"The decision tree recommends X"*
2. State the reason for deviation: *"We're deviating because Y"*
3. Document it as an ADR: `/adr [topic]`
4. Update Key Decisions in `PROJECT-CONTEXT.md`

A documented deviation is better than an undocumented one. The method supports exceptions — it just requires them to be explicit.

> 📝 *Artifact generated and maintained by the **OpenForge Agent** (Cursor Agent Mode) or manually by the team.*
> **Purpose:** Session compaction — lets any LLM resume a project with full context in < 10 seconds of reading.
> **Rules:** Key Decisions are append-only (never delete). Session Log keeps last 5 entries; older ones are compressed into Key Decisions. Update at session end.

---

# PROJECT-CONTEXT — [Project Name]

## Quick State

| Field | Value |
|-------|-------|
| **Status** | `[Planning / In Progress / Build / Validation / Production]` |
| **Current phase** | `[e.g. Phase 4 — Pipeline Planning]` |
| **Next action** | `[e.g. Activate Pipeline Planner with architecture-document.md]` |
| **Last updated** | `[YYYY-MM-DD]` |
| **Last session by** | `[engineer name or "Agent"]` |

---

## Decision Anchors

> ⚠️ Hard constraints. Every persona must respect these before making any recommendation.
> Set once (Phase 1–2). Change only via `/change` + explicit justification.

| Anchor | Value | Impact |
|--------|-------|--------|
| **Team size** | `[1 / 2–3 / 4–8 / 8+]` | Determines operational complexity ceiling |
| **Budget** | `[🟢 Unconstrained / 🟡 Moderate $X/mo / 🔴 Tight $X/mo]` | Hard cap on tool recommendations |
| **Cloud** | `[AWS / GCP / Azure / On-prem / Multi-cloud]` | Constrains managed service choices |
| **PII present** | `[Yes — categories: X / No]` | Mandates security + governance phases |
| **Target env** | `[POC / Staging / Production]` | Determines rigor level for all phases |
| **Latency req.** | `[Batch D-1 / Intraday / Near-real-time / Streaming]` | Eliminates streaming stack if batch is sufficient |

---

## Team & Stack

**Team size:** [N people] | **Budget level:** [🟢 None / 🟡 Moderate / 🔴 Tight — $X/mo]

**Core stack:**
- Orchestration: `[Dagster / Airflow / other]`
- Storage: `[S3 / GCS / ADLS / other]`
- Table format: `[Iceberg / Delta / Hudi / none]`
- Query engine: `[Trino / BigQuery / Spark / Athena / other]`
- Transformation: `[dbt / Spark / other]`
- Monitoring: `[Grafana / Prometheus / other]`

**PII present:** `[Yes — [categories] / No]` | **Target env:** `[POC / Staging / Production]`

---

## Artifacts

| Artifact | Status | Notes |
|----------|--------|-------|
| `data-product-brief.md` | `[✅ Approved / 🔄 Draft / ⏳ Pending / ❌ Stale]` | |
| `architecture-document.md` | `[✅ / 🔄 / ⏳ / ❌]` | |
| `cost-context.md` | `[✅ / 🔄 / ⏳ / ❌ / N/A]` | |
| `security-assessment.md` | `[✅ / 🔄 / ⏳ / ❌ / N/A]` | |
| `data-contract-[name].md` | `[✅ / 🔄 / ⏳ / ❌]` | |
| `governance-policy.md` | `[✅ / 🔄 / ⏳ / ❌]` | |
| `pipeline-spec.md` | `[✅ / 🔄 / ⏳ / ❌]` | |
| `quality-signoff.md` | `[✅ / 🔄 / ⏳ / ❌ / ⏳ Pending]` | |
| `security-signoff.md` | `[✅ / 🔄 / ⏳ / ❌ / N/A]` | |

---

## Key Decisions

> ⚠️ Append-only. Never remove entries. Add new ones at the bottom.

| Date | Decision | Rationale | Decided by |
|------|----------|-----------|------------|
| [YYYY-MM-DD] | [e.g. Use Iceberg over Delta] | [e.g. Multi-engine requirement, no Databricks lock-in] | [persona / engineer] |

---

## Open Items

> Items that need a decision or action before the project can proceed.

- [ ] [e.g. Confirm PII treatment for `user_email` — anonymize or pseudonymize?]
- [ ] [e.g. Get infrastructure budget approval for Kubernetes cluster]

---

## Session Log

> Keep the last 5 sessions. When a 6th entry is added, compress the oldest into Key Decisions and delete it from here.

### Session [N] — [YYYY-MM-DD] — [Engineer / Agent]

**Personas used:** [e.g. Orchestrator → Data Architect]
**Artifacts touched:** [e.g. architecture-document.md (created)]
**Key outcomes:**
- [e.g. Chose Iceberg + Trino as query layer]
- [e.g. Deferred security assessment — POC with no PII]

**Blockers / open questions:**
- [e.g. Need to confirm GCS bucket naming convention with infra team]

---

### Session [N-1] — [YYYY-MM-DD] — [Engineer / Agent]

**Personas used:** [...]
**Artifacts touched:** [...]
**Key outcomes:**
- [...]

**Blockers / open questions:**
- [...]

---

*[Add older sessions above this line, delete when compressed into Key Decisions]*

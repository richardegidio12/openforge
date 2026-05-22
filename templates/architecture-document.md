# Architecture Document
**Project:** [name — must match data-product-brief.md]
**Date:** [date]
**Responsible architect:** [name]
**Status:** Draft | Approved

---

## 1. Context
> Summary of the business problem (reference to the Data Product Brief).

[answer — 3-5 lines]

## 2. Data Flow Diagram

```
[Source 1] ──┐
              ├──► [Ingestion] ──► [Raw/Bronze] ──► [Silver] ──► [Gold] ──► [Consumer]
[Source 2] ──┘
```

> Use ASCII art or describe the flow in text. Suggested tools: draw.io, Mermaid, Excalidraw.

## 3. Architectural Decision Records (ADRs)

### ADR-001: Processing strategy
- **Decision:** [Batch / Micro-batch / Streaming]
- **Rationale:** [why this choice for this context]
- **Accepted trade-offs:** [what we are giving up]
- **Discarded alternative:** [what was considered and why it was not chosen]

### ADR-002: Storage
- **Decision:** [DW / Lakehouse / Hybrid]
- **Technology:** [BigQuery / Snowflake / S3+Delta / ...]
- **Rationale:** [...]
- **Accepted trade-offs:** [...]

### ADR-003: Data layers
- **Decision:** [raw→serving / bronze→silver→gold / other]
- **Rationale:** [...]
- **Adopted naming:** [define naming standard for schemas/buckets]

### ADR-004: Orchestration
- **Decision:** [Airflow / Dagster / Prefect / cron]
- **Rationale:** [...]
- **Accepted trade-offs:** [...]

### ADR-005: Transformation
- **Decision:** [dbt / PySpark / plain SQL / ...]
- **Rationale:** [...]
- **Accepted trade-offs:** [...]

### ADR-006: Serving
- **Decision:** [direct DW connection / API / semantic layer]
- **Rationale:** [...]

## 4. Full Stack
| Component | Chosen technology | Alternative considered |
|-----------|------------------|------------------------|
| Cloud provider | [e.g. GCP] | [e.g. AWS] |
| Storage / DW | [e.g. BigQuery] | [e.g. Snowflake] |
| Orchestration | [e.g. Dagster] | [e.g. Airflow] |
| Transformation | [e.g. dbt] | [e.g. Spark] |
| File format | [e.g. Parquet / Delta] | [e.g. CSV] |
| Data quality | [e.g. Great Expectations / dbt tests] | [...] |
| Catalog | [e.g. DataHub / dbt docs] | [...] |
| Monitoring | [e.g. Grafana / Monte Carlo] | [...] |

## 5. Cost Estimate
| Component | Estimated cost/month | Note |
|-----------|----------------------|------|
| Storage | [e.g. $50] | [e.g. 500GB on S3] |
| Compute | [e.g. $200] | [e.g. Dagster Cloud + dbt Cloud] |
| DW queries | [e.g. $100] | [e.g. BigQuery on-demand] |
| **Estimated total** | **[e.g. $350/month]** | |

## 6. Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [e.g. Volume grows 10x in 6 months] | Medium | High | [e.g. Architecture already uses partitioning; horizontal scaling available] |
| [e.g. Source X API has rate limit] | High | Medium | [e.g. Implement retry with exponential backoff] |

## 7. What is outside this architecture
- [e.g. "Real-time streaming — can be added in v2 if needed"]
- [e.g. "Multi-region — out of scope due to cost"]

## 8. Next steps
1. Review with Data Governance & Quality Advisor to define contracts
2. Set up environments (dev / staging / prod)
3. Start with Pipeline Planner to break down into stories

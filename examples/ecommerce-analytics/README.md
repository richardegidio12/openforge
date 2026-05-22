# Example: Sales Analytics — Sample Store

Complete example of FORGE applied to a real e-commerce analytics project.

## Context

**Company:** Sample Store — mid-sized B2C e-commerce
**Team:** 2 data engineers
**Problem:** Manual sales report exported from the ERP every Monday morning, taking 3h and generating errors
**Solution:** Automated daily pipeline with a Metabase dashboard available by 07:00

## Generated artifacts (in order of creation)

| Phase | Persona | Artifact |
|-------|---------|----------|
| 1 — Discovery | Data Product Strategist | [data-product-brief.md](data-product-brief.md) |
| 2 — Architecture | Data Architect | [architecture-document.md](architecture-document.md) |
| 2.5 — Cost Context | Platform FinOps Engineer | [cost-context.md](cost-context.md) |
| 2.6 — Security Assessment | Security Consultant | [security-assessment.md](security-assessment.md) |
| 3 — Governance | Gov & Quality Advisor | [data-contract-orders.md](data-contract-orders.md) |
| 3 — Governance | Gov & Quality Advisor | [governance-policy.md](governance-policy.md) |
| 4 — Planning | Pipeline Planner | [pipeline-spec.md](pipeline-spec.md) |
| 6 — Validation | Gov & Quality Advisor | [quality-signoff.md](quality-signoff.md) |
| 6.5 — Security Audit | Security Consultant | [security-signoff.md](security-signoff.md) |

## Stack used

- **Cloud:** GCP
- **Storage:** GCS (Bronze) + BigQuery (Silver/Gold)
- **Orchestration:** Dagster Cloud Serverless
- **Transformation:** dbt Core
- **BI:** Metabase
- **CI/CD:** GitHub Actions

## Outcome

- Pipeline running daily since 04/02/2024
- Analyst who did the manual report validated that numbers match (divergence < 0.5%)
- Commercial team accesses the dashboard at 07:00 without manual intervention
- Time saved: ~3h/week for the analyst

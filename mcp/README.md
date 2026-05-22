# OpenForge MCP Integrations

MCPs (Model Context Protocol) allow the OpenForge Agent to interact directly with your data infrastructure — running queries, checking pipeline status, inspecting logs, creating issues — without leaving the chat.

**Without MCPs:** Agent gives advice → you run the command → you paste results back.
**With MCPs:** Agent runs the command, reads the result, continues the diagnosis.

---

## Setup

MCPs are configured in Cursor's settings file. Location:
- macOS: `~/.cursor/mcp.json`
- Windows: `%APPDATA%\Cursor\mcp.json`

A template is provided at `mcp/cursor-mcp-config.json`. Copy it and fill in your credentials.

---

## Available integrations by group

| Group | MCPs | File |
|-------|------|------|
| **Code & Communication** | GitHub, Slack | `mcp/code-communication.md` |
| **Data Warehouse & Query** | BigQuery, PostgreSQL, Trino, Hive | `mcp/data-warehouse.md` |
| **Orchestration** | Dagster, Airflow, Flink | `mcp/orchestration.md` |
| **Observability** | Grafana, Prometheus, ELK Stack, Thanos | `mcp/observability-stack.md` |
| **Cloud Infrastructure** | EKS, AKS, GKE (Kubernetes) | `mcp/cloud-infra.md` |

---

## What the Agent can do with MCPs active

### Consulting mode (project-aware)
```
User: "Yesterday's revenue looks wrong in the dashboard"

Agent (with BigQuery MCP):
→ Runs freshness check query directly
→ Runs volume anomaly query
→ Checks dbt test results
→ "Confirmed: fct_orders has 12,847 records for yesterday, but
   reconciliation shows a 2.3% divergence vs ERP. Here's the
   breakdown by status..."
```

### Build mode (implementation)
```
User: "I just created the dbt model. Can you run the tests?"

Agent (with GitHub + dbt via Bash):
→ Runs dbt test --select fct_orders+
→ Reads test output
→ "2 tests failed: unique on order_id and expression_is_true on
   net_revenue >= 0. See the diagnosis..."
```

### Incident response
```
User: "Pipeline failed at 2am"

Agent (with Dagster + Grafana MCPs):
→ Reads last run logs from Dagster
→ Queries Grafana for error rate metric at 02:00
→ Checks Prometheus alert history
→ "The job failed at 02:17 with ConnectionRefused. Grafana shows
   the ERP had latency > 30s from 02:00. Likely a maintenance
   window..."
```

---

## Priority order for setup

If you're setting up for the first time, prioritize in this order:

1. **GitHub** — essential for artifact commits and PR creation
2. **BigQuery or PostgreSQL** — enables data diagnostics
3. **Dagster or Airflow** — enables pipeline monitoring
4. **Slack** — enables notifications from within sessions
5. **Grafana/Prometheus** — enables observability diagnostics
6. **Kubernetes** — enables infra management (advanced)

---

## Security note

MCPs have access to your infrastructure. Follow these rules:
- Use read-only credentials where possible (diagnostic MCPs don't need write)
- GitHub MCP: use a fine-grained PAT with minimum repo scopes
- BigQuery MCP: use a SA with `bigquery.dataViewer` + `bigquery.jobUser` only
- Postgres MCP: use a read-only user
- Never store credentials in the mcp.json — use environment variables: `$GITHUB_TOKEN`
- Add `mcp.json` to `.gitignore` if it contains credentials

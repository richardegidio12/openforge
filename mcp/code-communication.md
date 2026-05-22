# MCP: Code & Communication

## GitHub

**Package:** `@modelcontextprotocol/server-github` (official)

```bash
# Install (Cursor handles this automatically via npx)
# Just configure in ~/.cursor/mcp.json
```

**What the Agent can do:**
- Create and update files in the repository (commit artifacts directly)
- Open issues for technical debt, security findings, action items
- Create pull requests for pipeline changes
- Read existing code and PR comments for context
- Search code across the repository

**Usage in OpenForge sessions:**

```
# After generating an artifact
"Can you commit data-contract-orders.md to the repository and open a PR?"

Agent:
→ Creates branch: feature/add-orders-data-contract
→ Commits data-contract-orders.md
→ Opens PR with description linking to the phase and persona that generated it

# After a security assessment
"Create GitHub issues for the critical findings from the security assessment"

Agent:
→ Creates GitHub issue: [SEC-001] Configure GCP Secret Manager — Critical
→ Creates GitHub issue: [SEC-002] Split service accounts by component — Important
→ Tags with labels: security, data-platform, epic-0
```

**Setup:**
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
  }
}
```

**Required token scopes:**
- `repo` (read/write code and PRs)
- `issues` (create and update issues)
- Use a **fine-grained PAT** scoped to specific repositories

---

## Slack

**Package:** `@modelcontextprotocol/server-slack` (official)

**What the Agent can do:**
- Send notifications to channels
- Post incident updates during response sessions
- Notify the team when an artifact is generated or a risk is found
- Read channel history for context (e.g., what was discussed about this pipeline)

**Usage in OpenForge sessions:**

```
# Incident response
"Send an update to #data-incidents that the backfill finished and the data is correct"

Agent:
→ Posts to #data-incidents:
  ✅ [Resolved] fct_orders backfill complete.
  Data validated: freshness ✅ volume ✅ reconciliation ✅
  Total downtime: 5h 35min. Post-mortem scheduled Friday.

# Security finding
"Notify the #data-platform channel about the critical credentials finding"

Agent:
→ Posts to #data-platform:
  🔴 [Security] Critical finding in security assessment:
  ERP credentials found in docker-compose.yml (committed to repo).
  Action required: rotate credentials + configure Secret Manager.
  Owner: Rafael Torres | Story: SEC-001 | Due: this sprint
```

**Setup:**
```json
"slack": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-slack"],
  "env": {
    "SLACK_BOT_TOKEN": "$SLACK_BOT_TOKEN",
    "SLACK_TEAM_ID": "YOUR_TEAM_ID"
  }
}
```

**Required bot scopes:** `channels:read`, `chat:write`, `channels:history`

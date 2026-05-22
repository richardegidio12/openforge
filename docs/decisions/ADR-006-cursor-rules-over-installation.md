# ADR-006: .cursor/rules over installation scripts for IDE integration

**Date:** 2024-03-25
**Status:** Accepted
**Context:** How OpenForge integrates with developer tools

---

## Context

AI-assisted development tools (Cursor, Claude Code, etc.) support different integration patterns. The question is whether OpenForge should require installation into user projects (like BMAD v4's install scripts and bmad-core) or use a lighter approach.

---

## Decision

OpenForge uses a **`.cursor/rules/openforge.mdc` file** that lives in the OpenForge repository itself. Users add OpenForge as a workspace folder in Cursor, and the rule activates automatically. For project-local use, users copy the single rule file to their `.cursor/rules/` — one command, no scripts.

---

## Rationale

**1. Zero installation reduces friction to first use**
The target audience includes teams with no dedicated DevOps support. An install script that requires Node.js, specific file permissions, or project restructuring creates a barrier. A git clone + one file copy is universally accessible.

**2. The method should work without the IDE integration**
OpenForge's core value is the structured thinking, not the tool integration. A team using Claude.ai or ChatGPT directly, without Cursor, gets the full method by reading persona files and copying activation prompts. The Cursor integration is an accelerator, not a requirement.

**3. `.cursor/rules` files are readable and modifiable**
Users can read the rule file, understand what it does, and modify it for their context. An opaque installation script is a black box. OpenForge's philosophy of transparency extends to its tooling.

**4. Repository-local rule means updates are automatic**
When the OpenForge repository is updated, the rule file updates too. Users who clone OpenForge and pull updates get improved agent behavior without reinstalling anything.

**5. LLM-agnostic by design**
Installation scripts that generate `.claude/` directories or `.cursor/` configurations are tool-specific. OpenForge's primary interface (persona files + activation prompts) works with any LLM. The Cursor integration is one of several possible tool integrations, not the canonical one.

---

## Alternatives considered

### Installation script (like BMAD bmad-core)
- **Rejected for v1:** Adds complexity, creates version management overhead, and assumes users have the necessary tooling to run scripts. May be added in a future version for teams that want a more integrated experience.

### VS Code extension
- **Deferred:** An extension could provide a richer UI (persona selector, artifact viewer, context display). The investment is not justified for v1 — the method's value comes from the AI interactions, not the UI.

### Single activation mega-prompt (everything in one paste)
- **Rejected because:** A prompt containing all 9 personas would be enormous and would likely exceed context windows. Modular persona files are the right granularity.

---

## Consequences

- **Positive:** No installation. Clone + optional one-file copy. Works on any machine with Cursor.
- **Positive:** The method is tool-agnostic — works with any LLM, any interface.
- **Positive:** Rule file is readable, modifiable, and version-controlled.
- **Negative:** Cursor-specific features (Agent mode, MCP) are not available to users of other tools. Mitigated by manual mode documentation.
- **Negative:** The rule file approach may not work for all Cursor configurations. Mitigated by the manual activation prompt fallback.

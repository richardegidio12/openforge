# Contributing to OpenForge

Thank you for your interest in contributing! This project is open source and all contributions are welcome.

---

## What you can contribute

| Type | Examples |
|------|---------|
| **Persona improvements** | Sharper questions, clearer principles, new warning signals |
| **New templates** | Alternative formats for existing artifacts |
| **New examples** | Other domains: SaaS, logistics, healthcare, finance |
| **Stack adaptations** | Persona versions for Airflow, Spark, Databricks, etc. |
| **Fixes** | Errors, inconsistencies between personas, broken links |
| **Translations** | The method is in English — translations to other languages are welcome |

---

## How to contribute

### 1. Open an issue first

Before opening a PR, open an issue describing:
- What you want to change and why
- Whether it's a fix, improvement or new addition

This avoids duplicate work and ensures alignment before implementing.

### 2. Fork and branch

```bash
# Fork the repository on GitHub
git clone https://github.com/richardegidio12/openforge.git
cd openforge
git checkout -b my-contribution
```

### 3. Make your changes

Follow the project conventions:
- Personas in `personas/` with numeric prefix (`00-`, `01-`, etc.)
- Templates in `templates/` — no example content, only placeholders
- Examples in `examples/{project-name}/` with all artifacts filled in
- Language: English

### 4. Open the PR

- Clear and descriptive title
- Describe what changed and why
- Reference the related issue

---

## Guiding principles for contributions

1. **Practicality over perfection** — contributions that real teams can use today are more valuable than theoretically perfect frameworks
2. **Calibrated for small teams** — the method is built for 1–10 people, not large enterprises
3. **Stack-agnostic personas** — personas should not recommend a specific stack, but offer decision frameworks
4. **Consistency across artifacts** — a change in one persona may impact the artifact consumed by the next persona

---

## Questions?

Open an issue with the `question` label or reach out via GitHub Discussions.

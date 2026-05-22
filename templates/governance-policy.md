# Data Governance Policy
**Project:** [name]
**Date:** [date]
**Responsible:** [name — data owner or tech lead]
**Status:** Draft | Approved

---

## 1. Dataset Ownership Matrix

| Dataset | Layer | Producer (technical owner) | Primary consumer(s) | Incident escalation |
|---------|-------|---------------------------|---------------------|---------------------|
| [e.g. orders] | Gold | [name / contact] | [team / area] | [name / channel] |
| [e.g. customers] | Gold | [name / contact] | [team / area] | [name / channel] |

---

## 2. Data Classification

| Classification | Definition | Examples | Access control |
|----------------|------------|----------|----------------|
| Public | Can be shared externally | Aggregated metrics without PII | Open |
| Internal | Internal use only | Operational reports | Corporate authentication |
| Confidential | Restricted to specific teams | Financial data, salaries | Role-based (RBAC) |
| Sensitive / PII | Personal data — principle of least privilege | SSN, email, phone, IP | Audited access + justification |

---

## 3. Identified PII Fields

| Dataset | Layer | Column | PII type | Treatment applied | Who can access raw data |
|---------|-------|--------|----------|-------------------|-------------------------|
| [e.g. customers] | Bronze | [e.g. customer_ssn] | SSN | Removed in Silver — not exposed | Technical owner only |
| [e.g. customers] | Bronze | [e.g. customer_email] | Email | Hashed (SHA-256) in Silver | Technical owner only |
| [e.g. orders] | Bronze | [e.g. customer_phone] | Phone | Removed in Silver | Technical owner only |

---

## 4. Access Policy by Layer

| Layer | Who can read | Who can write | Note |
|-------|-------------|---------------|------|
| Bronze (raw) | [e.g. data engineers only] | Ingestion pipeline (service account) | Contains PII — restricted access |
| Silver (clean) | [e.g. data team + data scientists] | Transformation pipeline (service account) | PII treated |
| Gold (serving) | [e.g. all analysts + BI tools] | dbt pipeline (service account) | No PII |

---

## 5. Retention Policy

| Data type | Retention | Action on expiry | Responsible |
|-----------|-----------|------------------|-------------|
| Bronze (raw data with PII) | [e.g. 90 days] | Automatic deletion | [technical owner] |
| Silver (processed data) | [e.g. 2 years] | Anonymize and archive | [technical owner] |
| Gold (analytical data) | [e.g. 3 years] | Anonymize and archive | [technical owner] |
| Pipeline logs | [e.g. 30 days] | Automatic deletion | [technical owner] |

---

## 6. Legal Basis (GDPR/LGPD)

| Data | Legal basis | Article |
|------|-------------|---------|
| [e.g. customer data for sales analysis] | [e.g. Contract execution] | [e.g. Art. 7, V] |
| [e.g. data for behavioral analysis] | [e.g. Legitimate interest] | [e.g. Art. 7, IX] |

> 📌 Consult the DPO (Data Protection Officer) if one exists at the company before finalizing this section.

---

## 7. Quality Incident Process

| Step | Action | Responsible | Deadline |
|------|--------|-------------|----------|
| 1 | Alert triggered (automatic or manual) | System / any team member | Immediate |
| 2 | Technical owner notified | System (configured alert) | < 15 min |
| 3 | Impact assessment: which consumers are affected? | Technical owner | < 1 hour |
| 4 | Communication to impacted consumers | Technical owner | < 2 hours |
| 5 | Fix and re-validation | Technical owner | Per severity |
| 6 | Post-mortem (if production impact > [threshold]) | Data team | < 48 hours after resolution |

**Incident channel:** [e.g. #data-platform on Slack]
**Post-mortem threshold:** [e.g. incorrect data consumed for > 2 hours in production]

---

## 8. Schema Change Process

| Change type | Notice period | Channel | Approval required |
|-------------|---------------|---------|-------------------|
| Breaking (column removal, type change) | 2 weeks | [channel] + email to owners | Technical owner + primary consumer |
| Non-breaking (new column, new enum value) | 3 business days | [channel] | Technical owner |
| Hotfix (critical bug fix) | Immediate with simultaneous communication | [channel] | Technical owner |

---

## 9. New Member Onboarding Process

When a new engineer or analyst joins the team:

- [ ] Request access to the Gold dataset via [channel]
- [ ] Technical owner grants `dataViewer` role in BigQuery/DW
- [ ] New member reads the project `HOW-TO-USE.md`
- [ ] New member reads the data contracts for the datasets they will consume
- [ ] New member is added to [alerts channel]

---

## 10. Policy Review

- **Review frequency:** [e.g. semi-annual or when there is a significant scope change]
- **Next review:** [date]
- **Version history:**

| Version | Date | Author | What changed |
|---------|------|--------|--------------|
| 1.0 | [date] | [name] | Initial version |

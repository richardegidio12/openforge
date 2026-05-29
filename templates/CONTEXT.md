# Data Domain Context
**Project:** [name]
**Domain:** [e.g.: e-commerce / fintech / healthcare / logistics / SaaS analytics]
**Updated:** [date]
**Status:** Living document — update as the domain evolves

> This document is the shared glossary for the data platform. Every persona, pipeline, and model references it.
> When a term means different things to different teams, document ALL meanings and declare which one is canonical.

---

## Business entities

> List the core objects the business cares about. These map directly to data contracts and Silver tables.

| Entity | Definition | Canonical source | Notes |
|--------|-----------|-----------------|-------|
| [e.g.: Order] | [e.g.: A confirmed purchase request from a customer] | [e.g.: ERP / Salesforce] | [e.g.: Draft orders are excluded from analytics] |
| [e.g.: Customer] | [e.g.: Any entity that has placed at least one paid order] | [e.g.: CRM] | [e.g.: Internal test accounts excluded — filter by `is_internal = false`] |
| [e.g.: Product] | [e.g.: A sellable unit with a unique SKU] | [e.g.: Catalog service] | [e.g.: Bundles count as one product] |

---

## Key metrics and definitions

> Business metrics that the team must agree on before modeling begins.
> Ambiguous metrics (different teams calculate them differently) must be resolved here.

| Metric | Definition | Formula | Scope | Exclusions |
|--------|-----------|---------|-------|-----------|
| [e.g.: MRR] | [e.g.: Monthly Recurring Revenue] | [e.g.: SUM(active_subscription_value) per month] | [e.g.: Paid subscriptions only] | [e.g.: Trials, freemium, internal accounts] |
| [e.g.: Churn rate] | [e.g.: % of paying customers who cancelled in a period] | [e.g.: churned_customers / active_customers_start_of_period] | [e.g.: Monthly] | [e.g.: Customers who upgraded/downgraded are NOT churned] |
| [e.g.: GMV] | [e.g.: Gross Merchandise Value — total transaction value] | [e.g.: SUM(order_total)] | [e.g.: All completed orders] | [e.g.: Refunded orders are netted out] |

---

## Business rules

> Rules that affect data processing, filtering, or calculation. Document the source of truth for each.

| Rule | Description | Applies to | Source of truth |
|------|------------|-----------|----------------|
| [e.g.: Active customer] | [e.g.: A customer with at least one order in the last 365 days] | [e.g.: Customer entity, churn models] | [e.g.: Product team definition — v2 approved 2024-03] |
| [e.g.: Revenue recognition] | [e.g.: Revenue recognized on shipment date, not order date] | [e.g.: All revenue metrics] | [e.g.: Finance team — aligned with IFRS 15] |
| [e.g.: Test/internal orders] | [e.g.: Orders with `customer_email LIKE '%@company.com'` are excluded] | [e.g.: All order-based metrics] | [e.g.: Analytics team convention — see ADR-XXX] |

---

## Ambiguous terms (resolved)

> Terms that caused confusion or had conflicting definitions. Document the resolution so it doesn't come up again.

| Term | Team A definition | Team B definition | Canonical definition | Decided by | Date |
|------|------------------|------------------|---------------------|-----------|------|
| [e.g.: "Active user"] | [e.g.: Logged in last 30 days] | [e.g.: Made a transaction last 30 days] | [e.g.: Logged in last 30 days — transactions tracked separately as "paying user"] | [e.g.: Product + Data leads] | [date] |

---

## Data sources

> Where data comes from. Each source maps to a Bronze layer table.

| Source | Type | What it contains | Refresh frequency | Owner | Notes |
|--------|------|-----------------|------------------|-------|-------|
| [e.g.: Salesforce] | [e.g.: SaaS CRM] | [e.g.: Leads, opportunities, accounts, contacts] | [e.g.: Every 4h] | [e.g.: Sales team] | [e.g.: Stage mapping: SQL→MQL→SAL→SQL→Closed Won] |
| [e.g.: PostgreSQL (ERP)] | [e.g.: Internal DB] | [e.g.: Orders, products, inventory, fulfillment] | [e.g.: CDC near-real-time] | [e.g.: Engineering] | [e.g.: Schema changes require 2-week notice — data contract SLA] |
| [e.g.: Stripe] | [e.g.: Payment API] | [e.g.: Payments, subscriptions, invoices, refunds] | [e.g.: Webhooks + daily reconciliation] | [e.g.: Finance] | [e.g.: Use `created` not `updated` for event ordering] |

---

## Known data quality issues

> Existing problems in source data that the platform must handle or document.

| Source | Issue | Impact | Current handling | Planned fix | Owner |
|--------|-------|--------|-----------------|------------|-------|
| [e.g.: ERP orders] | [e.g.: ~2% of orders have NULL `shipped_at` despite `status = 'shipped'`] | [e.g.: Delivery time calculations are skewed] | [e.g.: Excluded from delivery SLA metrics] | [e.g.: Data fix in ERP Q3 — tracked in JIRA-1234] | [e.g.: Backend team] |
| [e.g.: Salesforce leads] | [e.g.: `lead_source` has 40+ inconsistent values after CRM migration] | [e.g.: Marketing attribution is unreliable] | [e.g.: Mapped to 8 canonical values in Silver transformation] | [e.g.: CRM cleanup in progress] | [e.g.: Sales Ops] |

---

## PII inventory

> Every field containing Personal Identifiable Information. Feeds data contracts and governance policy.

| Table/Source | Field | PII type | Treatment | Retention |
|-------------|-------|----------|-----------|-----------|
| [e.g.: customers] | [e.g.: email] | [e.g.: Direct identifier] | [e.g.: Hash in Silver, remove in Gold] | [e.g.: 5 years per legal] |
| [e.g.: orders] | [e.g.: shipping_address] | [e.g.: Direct identifier] | [e.g.: Keep in Silver, mask in Gold] | [e.g.: 7 years per LGPD Art. 16] |

---

## Regulatory context

> Legal and compliance constraints that affect data handling.

| Regulation | Scope | Key requirements | Responsible |
|-----------|-------|-----------------|------------|
| [e.g.: LGPD] | [e.g.: All Brazilian user data] | [e.g.: Purpose limitation, consent, 72h breach notification] | [e.g.: DPO: legal@company.com] |
| [e.g.: SOC2 Type II] | [e.g.: SaaS product data] | [e.g.: Audit logging, access controls, change management] | [e.g.: Head of Engineering] |

---

## Open questions

> Domain questions that are unanswered or in progress. Each one is a risk until resolved.

| Question | Impact if unresolved | Owner | Status | Target date |
|---------|---------------------|-------|--------|------------|
| [e.g.: "Should refunded orders count toward GMV?"] | [e.g.: GMV metric could be overstated by 3-5%] | [e.g.: Finance + Product] | [e.g.: In discussion] | [date] |

---

*This document is maintained by the data team. Updates require review from the business owner of the affected domain.*

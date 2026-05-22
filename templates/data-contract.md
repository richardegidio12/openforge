# Data Contract
**Dataset:** [name]
**Project:** [project name]
**Version:** 1.0
**Creation date:** [date]
**Status:** Draft | Active | Deprecated

---

## Ownership
| Role | Name | Contact |
|------|------|---------|
| Producer (technical owner) | [name] | [slack/email] |
| Primary consumer | [name / team] | [slack/email] |
| Incident escalation | [name] | [slack/email] |

## Schema
| Column | Type | Nullable | Description | PII? | Example |
|--------|------|----------|-------------|------|---------|
| [e.g. order_id] | STRING | NO | Unique order identifier | No | "ORD-00123" |
| [e.g. customer_email] | STRING | NO | Customer email | **YES** | [anonymized] |
| [e.g. amount] | FLOAT | NO | Order amount in USD | No | 149.90 |
| [e.g. status] | STRING | NO | Order status | No | "completed" |
| [e.g. created_at] | TIMESTAMP | NO | Creation timestamp | No | 2024-01-15T10:30:00Z |

## Freshness SLA
- **Update frequency:** [e.g. daily]
- **Availability time:** [e.g. data for day D available by 08:00 on D+1]
- **Maximum delay tolerance:** [e.g. up to 2h delay is acceptable]
- **How to measure:** [e.g. MAX(created_at) must be < NOW() - 26h]

## Quality Expectations

### Completeness
| Column | Rule | Threshold |
|--------|------|-----------|
| order_id | Never null | 100% |
| amount | Never null | 100% |
| status | Never null | 100% |

### Expected volume
- **Minimum per business day:** [e.g. 500 records]
- **Expected maximum:** [e.g. 50,000 records]
- **Alert if out of range:** Yes

### Uniqueness
- **Primary key:** [e.g. order_id]
- **Duplicates accepted:** No — dedup applied in Silver

### Validity
| Rule | Expression | Action if violated |
|------|------------|--------------------|
| Positive amount | amount > 0 | Alert + quarantine record |
| Valid status | status IN ('pending', 'completed', 'cancelled') | Alert |
| No future date | created_at <= NOW() | Alert + investigation |

### Consistency
- [e.g. "Sum of amount per day must match ERP report with 0.01% tolerance"]

## Privacy Policy
- **Contains PII:** [Yes / No]
- **Identified PII fields:** [e.g. customer_email, customer_ssn]
- **Treatment applied:** [e.g. "Email hashed with SHA-256 in Silver layer; SSN removed"]
- **Who can access raw data (with PII):** [e.g. only engineers with Bronze access]
- **Retention:** [e.g. data kept for 2 years, then permanently anonymized]
- **Legal basis (GDPR/LGPD):** [e.g. contract execution — Art. 7, V]

## Access Policy
| Layer | Who can read | Who can write |
|-------|-------------|---------------|
| Bronze (raw) | Data team | Ingestion pipeline |
| Silver (clean) | Data team + Data Scientists | Transformation pipeline |
| Gold (serving) | All analysts + BI tools | Modeling pipeline |

## Change Policy
- **Breaking changes:** notify consumers 2 weeks in advance
- **Non-breaking changes:** notify consumers 3 days in advance
- **Notification channel:** [e.g. #data-platform on Slack]
- **Versioning:** semantic tag in the repository

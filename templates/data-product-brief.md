# Data Product Brief
**Project:** [project name]
**Date:** [date]
**Business owner:** [name / title]
**Status:** Draft | Approved

---

## 1. Business Problem
> What is happening (or failing to happen) that motivates this project?

[answer]

## 2. Decisions this data will enable
> List the concrete decisions that will be made based on this data.

- Decision 1: [e.g. "the marketing team will segment campaigns based on RFM"]
- Decision 2: ...

## 3. Consumers
| Consumer | Usage type | Tool | Access frequency |
|----------|------------|------|------------------|
| [e.g. Marketing analyst] | [e.g. Exploratory analysis] | [e.g. Looker] | [e.g. Daily] |

## 4. Refresh requirements
- **Frequency:** [e.g. daily, hourly, near-real-time]
- **Tolerance window:** [e.g. "data can be up to 2h delayed without impact"]
- **Critical time:** [e.g. "must be updated by 8am for the morning report"]

## 5. Estimated volume
- **Records per day:** [e.g. ~500k events]
- **Expected growth:** [e.g. 20% per month]
- **Seasonality:** [e.g. peak at end of month, 3x normal volume]

## 6. Data sources
| Source | Type | Owner | Access available? | Known quality? |
|--------|------|-------|-------------------|----------------|
| [e.g. Sales PostgreSQL] | [e.g. relational database] | [e.g. engineering team] | [e.g. Yes] | [e.g. Good, but has duplicates] |

## 7. Constraints and risks
- **Privacy/GDPR:** [e.g. "customer SSN and email present — anonymization required"]
- **Access:** [e.g. "ERP API requires vendor approval — uncertain timeline"]
- **Source quality:** [e.g. "orders table has ~3% records without status"]
- **Deadline:** [e.g. "first report expected for the board in 6 weeks"]
- **Other risks:** [...]

## 8. Success criteria
> How will we know this project was successful?

[e.g. "Analysts can generate the weekly churn report without manual intervention, with data updated to D-1"]

## 9. What is OUT of scope
> Important for setting expectations.

- [e.g. "Predictive churn analysis is out of scope for this phase"]
- [e.g. "Historical data prior to 2022 will not be migrated"]

## 10. Notes and observations
[free-form notes from the interview, identified warning signs, suggested next steps]

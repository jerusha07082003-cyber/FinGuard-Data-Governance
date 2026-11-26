# Governance specification (demo)

**Purpose:** make synthetic purchase data fit for downstream risk review. The dataset is not Amex data and is not representative of real customer activity.

## Ownership and controls

| Asset | Proposed accountable owner | Proposed steward | Classification |
| --- | --- | --- | --- |
| Raw CSV | Transaction data product owner | Ingestion analyst | Synthetic; restricted in a real system |
| Accepted transactions | Transaction data product owner | Data quality analyst | Masked synthetic; internal |
| Exceptions / quality results | Data governance lead | Data quality analyst | Internal |
| Risk review queue | Risk product owner | Risk analyst | Internal; not fraud labels |

These are proposed assignments, not real organizational controls. In GCP, use BigQuery Job User at project scope for query execution, dataset-level Data Viewer for analysts and Data Editor for the ingestion identity. Creating datasets requires additional project permissions. Avoid broad Owner roles for routine processing; do not grant public access. The demo does not automatically provision IAM or enforce enterprise policies. Review dataset permissions in the console.

## Lineage and quality policy

Raw CSV → normalized Pandas rows → rule evaluation → accepted masked CSV / exception references → SQLite SQL risk calculation → dashboard. Optional BigQuery batch load receives only accepted masked rows, exception references and quality results; BigQuery SQL re-computes risk flags independently.

The first otherwise-valid transaction per transaction ID is retained. Reject rather than impute missing IDs or invalid amounts. Currency, category and transaction type are standardized before checks. A row can fail multiple rules; duplicate counts are evaluated among otherwise valid records. Overall acceptance rate = accepted / input; not a measure of real-world accuracy. True factual accuracy is not measurable without an authoritative external source. Reconciliation: input = accepted + rejected.

Risk rules: amount > INR 50,000, or >=3 accepted purchases for the same customer in an inclusive trailing 60-minute window. Window peers at the same timestamp count together. These are review heuristics, not proof of fraud or a trained model; no accuracy or precision/recall claim.

## Data dictionary

| Field | Type | Meaning / constraint |
| --- | --- | --- |
| source_row | integer | 1-based position in raw file; lineage reference |
| transaction_id | string | TX + five digits; unique among accepted rows |
| customer_id | string | CUST + four digits; required |
| amount | integer | Whole INR rupees; positive purchase amount; demo cap below 1 trillion |
| currency | string | INR only |
| merchant_category | string | Food, Shopping, Travel, Healthcare, Entertainment, Groceries |
| transaction_type | string | Purchase only; refunds outside scope |
| timestamp | timestamp | Purchase time normalized to UTC; naive demo timestamps interpreted as UTC |
| email | string | Artificial address; removed from all curated outputs |
| email_masked | string | Constant redacted placeholder, not anonymization |
| failed_rules | string | Pipe-separated IDs of failed checks |
| purchases_60m | integer | Accepted purchases in trailing 60 minutes |
| risk_status | string | Review or Routine |

## Audit and retention

Each run records UTC time, UUID, source SHA-256, rule version and reconciliation metrics. Latest output tables are replaced each run; local JSONL history is append-only by convention, not tamper-proof. Demo BigQuery tables default to 60-day expiration on newly created datasets. For production, add authenticated access, encrypted restricted raw/quarantine storage, retention policy, immutable logs, orchestrated atomic runs, monitoring and human review. Never upload real financial data to this demo.

# Explain FinGuard in an interview

**30-second pitch (after you run and understand it):** I built a synthetic financial data governance pipeline. Python and Pandas validate and standardize purchase records, quarantine bad rows, redact synthetic emails and generate audit metrics. SQLite SQL calculates review flags from purchase value and trailing customer activity. I documented lineage, ownership and quality rules and built a dashboard. [Only after executing cloud steps: I also loaded masked records into BigQuery and reproduced risk and quality analytics using SQL.]

## Five questions to master first

1. **Why synthetic data?** No real customer information; intentionally injected defects give predictable quality checks. It does not model actual fraud prevalence.
2. **Why 97.03%?** 9,800 accepted / 10,100 input = 97.03%. 300 rejected = 100 missing IDs + 100 invalid amounts + 100 duplicate copies. Acceptance is not accuracy.
3. **How do you identify duplicates?** Normalize first, validate required fields, then keep the first otherwise-valid transaction ID. Invalid rows go to exceptions. Other deduplication policies could use event time or source priority.
4. **How does SQL identify risk?** A window counts accepted purchases for each customer in the preceding 3,600 seconds including the current row. A high value or three or more purchases triggers review. False positives are possible; rules are not predictions.
5. **What is governance?** Ownership, standards, access and traceability. This demo documents proposed owners/stewards, checks, data lineage and run history. Real enterprise IAM and immutable audit logs are outside scope.

## Learn the code in order

- `finguard/generate.py`: dictionaries, loops, random seed, CSV.
- `finguard/quality.py`: DataFrames, missing values, Boolean masks, schema, deduplication, masking.
- `finguard/pipeline.py`: SQL tables, output files, reconciliation, hash and run ID.
- `sql/local_risk.sql`: CTE, PARTITION BY, RANGE window, CASE.
- `app.py`: Streamlit tabs, filters, charts and CSV downloads.
- `cloud_upload.py`: ADC authentication, explicit BigQuery schema, batch load jobs, query jobs.

## Resume wording (only after personally running and understanding)

**FinGuard — Financial Data Governance & Risk Analytics | Python, SQL, Pandas, SQLite, Streamlit**
- Implemented a synthetic transaction validation pipeline processing 10,100 records, quarantining 300 records with known data defects and retaining 9,800 accepted records.
- Automated schema checks, deduplication, email masking, exception reports and run-level audit metrics; used SQL window functions to flag 54 transactions for review.
- Built an interactive dashboard and documented data lineage, quality rules and proposed access controls; verified pipeline behavior with automated tests.

After successful BigQuery execution, add GCP / BigQuery and a bullet: Loaded masked transaction and quality tables into Google BigQuery and reproduced risk analytics, category aggregations and rule-level reconciliation using Standard SQL. Do not claim production cloud experience, real fraud detection accuracy, or professional ownership of enterprise assets.

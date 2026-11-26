# BigQuery setup (no billing route first)

1. Sign into https://console.cloud.google.com/bigquery. Create a dedicated project (e.g. display name FinGuard Demo). Copy its **project ID**, not display name. Use the BigQuery sandbox if available. Do not attach billing merely to complete this demo.
2. Open BigQuery Studio. In Explorer, select the project's menu > Create dataset. Dataset ID: `finguard`, location: `US` multi-region. Keep the sandbox expiration setting (typically 60 days).
3. Run the local pipeline first. Create three tables in the dataset using Create table > Upload, file format CSV, source files from `outputs/`, destination names below. In Advanced options set header rows to skip = 1. Use explicit schema (Edit as text / fields) in the listed order. Do not upload the raw input CSV.

| Table / file | Fields (in order) |
| --- | --- |
| clean_transactions.csv | source_row INTEGER, transaction_id STRING, customer_id STRING, amount INTEGER, currency STRING, merchant_category STRING, transaction_type STRING, timestamp TIMESTAMP, email_masked STRING |
| exceptions.csv | source_row INTEGER, transaction_id STRING, failed_rules STRING |
| quality_results.csv | rule_id STRING, dimension STRING, description STRING, failed_rows INTEGER, evaluated_rows INTEGER |

4. Click Compose new query. Paste `sql/bigquery_quality.sql`, replace `YOUR_PROJECT_ID` with your actual project ID, and Run. Repeat for summary, reconcile and risk files. Confirm 100 failures each for customer_id, amount and duplicate_id; all reconciliation rows true; risk query returns 9,800 records of which 54 are Review. The risk query shows rows, not aggregate counts; to count review statuses wrap its query (without trailing semicolon) in `SELECT risk_status, COUNT(*) FROM (...) GROUP BY risk_status`.
5. Save screenshots of your dataset tables and successful queries (hide personal account details). Explain the SQL window calculation and compare counts with your local dashboard.

## Optional Python API route

Instead of manual uploads, install the Google Cloud CLI (https://docs.cloud.google.com/sdk/docs/install), then in a local terminal:

```
python -m pip install -r requirements-cloud.txt
gcloud init
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
python cloud_upload.py --project YOUR_PROJECT_ID --location US
```

The BigQuery API must be enabled, and your account must have permissions to create the dataset/tables and run jobs. If asked to set a quota project, use `gcloud auth application-default set-quota-project YOUR_PROJECT_ID` if permitted. Never commit credentials. The uploader refuses to overwrite existing demo tables unless you pass `--replace`; use that flag only for your own dedicated demo tables. If you already uploaded manually, simply run SQL in the console instead. Cloud script is provided but not executed in the build environment.

Sandbox supports batch loads and read queries; it has free quota and limits (including DML and streaming restrictions and expiration). Query usage and billing depend on your project. Do not enable billing unless you understand charges; set quotas/cost controls if you do. The uploader uses a 100 MiB maximum-bytes-billed guard per query. Clean up by deleting only your dedicated demo dataset when finished, after saving screenshots.

Official references: https://docs.cloud.google.com/bigquery/docs/sandbox ; https://docs.cloud.google.com/bigquery/docs/authentication ; https://docs.cloud.google.com/bigquery/docs/reference/libraries .

# FinGuard — Financial Data Governance & Fraud Risk Analytics

Portfolio project for data governance / analytics roles. Synthetic financial purchases only; not affiliated with American Express. Local pipeline is runnable independently of cloud credentials. The optional BigQuery path is a batch integration, not a production deployment.

## Start here (Windows / VS Code)

1. Extract the ZIP, open the **FinGuard** folder in VS Code, then Terminal > New Terminal. Use Python 3.11 or 3.12. Check `python --version` (or `py --version`).
2. Create a virtual environment: `python -m venv .venv`.
3. PowerShell: `.\.venv\Scripts\Activate.ps1`. If blocked, use Command Prompt and run `.venv\Scripts\activate.bat`. macOS/Linux: `source .venv/bin/activate` (use python3 to create venv if needed).
4. `python -m pip install -r requirements.txt`
5. `python generate_data.py`
6. `python run_pipeline.py`
7. `python -m pytest -q`
8. `python -m streamlit run app.py` — open the local URL printed in the terminal (usually http://localhost:8501). Stop with Ctrl+C.

Alternative without activation (PowerShell): `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and use that executable instead of python for the other commands.

**Instant preview:** open `dashboard_preview.html` in a browser (double-click); it is a standalone interactive snapshot from the included run. To refresh after running the pipeline, run `python build_preview.py`. No Streamlit or internet required to open the preview. If Streamlit installation fails, the pipeline only requires Pandas: `python -m pip install pandas pytest`.

## Expected results for seed 42

- Input: 10,100 rows (10,000 original + 100 copied)
- Accepted: 9,800; rejected: 300; acceptance: 97.03%
- 100 missing customer IDs, 100 negative purchase amounts, 100 extra duplicate rows
- 54 accepted records flagged for review: 50 high value, 4 rapid activity (no overlap in this run)
- No true fraud labels; counts are review flags, not prediction accuracy.

## Cloud (optional, needed to demonstrate hands-on GCP)

Follow [docs/CLOUD_SETUP.md](docs/CLOUD_SETUP.md) to create a BigQuery sandbox, load the three processed tables, run four SQL queries, and optionally upload using Python ADC. The Streamlit dashboard reads local outputs, not BigQuery directly. Cloud execution is not verified without your credentials.

## Repository guide

| File | Purpose |
| --- | --- |
| generate_data.py / finguard/generate.py | Generate reproducible synthetic data |
| run_pipeline.py / finguard/pipeline.py | Validate, persist, run SQL, export metrics and audit |
| finguard/quality.py | Rule engine, masking, exception handling |
| sql/local_risk.sql | SQLite window function for risk review |
| sql/bigquery_*.sql | BigQuery SQL quality, risk, summary, reconciliation |
| cloud_upload.py | Optional ADC-authenticated cloud batch uploader and query runner |
| app.py | Streamlit dashboard |
| build_preview.py | Offline HTML snapshot generator |
| tests/test_pipeline.py | Automated tests |
| docs/GOVERNANCE.md | Business rules, lineage, dictionary, roles, limitations |
| docs/INTERVIEW.md | Explain the project to recruiters |
| data/transactions.csv | Included synthetic input |
| outputs/ | Included latest outputs and local audit snapshot |

## Make it public (portfolio)

Create a new GitHub repository, open this folder in VS Code and run:

```
git init
git add .
git commit -m "Build FinGuard financial data governance pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/finguard.git
git push -u origin main
```

Replace YOUR_USERNAME and authenticate when prompted. Ensure no credentials, .venv, real data or secrets are committed. GitHub Actions runs tests on pushes. For a public dashboard, connect the repo at https://share.streamlit.io/ and choose `app.py` as the entrypoint. The local synthetic snapshot is included; no cloud keys needed. Hosting requires your account, and public visitors can interact with the demo. The offline HTML can also be shared directly. See https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app.

This is an educational prototype: no real customer data, fraud model, production IAM, enterprise orchestration, authenticated dashboard or transactional multi-user state. The local dashboard re-run button replaces latest outputs; do not expose it as a production service.

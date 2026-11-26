"""Optional: load processed CSVs to BigQuery and execute read-only SQL checks.
Requires ADC and permission to create datasets/tables/jobs. Never uploads raw emails.
"""
import argparse
import re
from pathlib import Path
from datetime import datetime,timedelta,timezone
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

ROOT=Path(__file__).resolve().parent
SCHEMAS={
 'clean_transactions':[('source_row','INT64'),('transaction_id','STRING'),('customer_id','STRING'),('amount','INT64'),('currency','STRING'),('merchant_category','STRING'),('transaction_type','STRING'),('timestamp','TIMESTAMP'),('email_masked','STRING')],
 'exceptions':[('source_row','INT64'),('transaction_id','STRING'),('failed_rules','STRING')],
 'quality_results':[('rule_id','STRING'),('dimension','STRING'),('description','STRING'),('failed_rows','INT64'),('evaluated_rows','INT64')],
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',required=True,help='Google Cloud project ID')
    p.add_argument('--location',default='US',help='Dataset location; must match existing dataset')
    p.add_argument('--replace',action='store_true',help='Explicitly allow replacing the three demo tables')
    a=p.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]',a.project): p.error('Use a valid Google Cloud project ID')
    client=bigquery.Client(project=a.project,location=a.location)
    dsid=f'{a.project}.finguard'
    dataset=bigquery.Dataset(dsid); dataset.location=a.location
    dataset.default_table_expiration_ms=60*24*60*60*1000
    dataset=client.create_dataset(dataset,exists_ok=True)
    if dataset.location.upper()!=a.location.upper(): raise ValueError(f'Existing dataset location is {dataset.location}')
    for name in SCHEMAS:
        if not (ROOT/'outputs'/f'{name}.csv').exists(): raise FileNotFoundError('Run python run_pipeline.py first')
        if not a.replace:
            try: client.get_table(f'{dsid}.{name}')
            except NotFound: pass
            else: raise RuntimeError(f'{name} already exists. Use --replace only to replace your demo tables.')
    for name,fields in SCHEMAS.items():
        cfg=bigquery.LoadJobConfig(schema=[bigquery.SchemaField(n,t) for n,t in fields],source_format=bigquery.SourceFormat.CSV,skip_leading_rows=1,write_disposition='WRITE_TRUNCATE' if a.replace else 'WRITE_EMPTY')
        # Explicit schema is in the same order as the CSV output.
        with (ROOT/'outputs'/f'{name}.csv').open('rb') as f:
            job=client.load_table_from_file(f,f'{dsid}.{name}',job_config=cfg,location=a.location)
            job.result()
        print(f'Loaded {client.get_table(f"{dsid}.{name}").num_rows:,} rows into {name}')
    for name in ['quality','summary','reconcile','risk']:
        sql=(ROOT/'sql'/f'bigquery_{name}.sql').read_text().replace('YOUR_PROJECT_ID',a.project)
        if name=='risk': sql=f"SELECT risk_status, COUNT(*) AS records FROM ({sql.rstrip().rstrip(';')}) GROUP BY risk_status"
        job=client.query(sql,job_config=bigquery.QueryJobConfig(maximum_bytes_billed=100*1024*1024),location=a.location)
        print(f'\n{name.upper()} | job_id={job.job_id}')
        for row in job.result(): print(dict(row))

if __name__=='__main__': main()

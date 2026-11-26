"""Run validation, local SQL risk analytics, and produce an audit snapshot."""
import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import pandas as pd
from .generate import ROOT, generate
from .quality import validate


def run(input_path=None, output_dir=None):
    source = Path(input_path or ROOT/'data'/'transactions.csv')
    out = Path(output_dir or ROOT/'outputs')
    out.mkdir(parents=True,exist_ok=True)
    if not source.exists():
        source.parent.mkdir(parents=True,exist_ok=True)
        generate().to_csv(source,index=False)
    raw = pd.read_csv(source,dtype={'transaction_id':'string','customer_id':'string','email':'string'})
    clean, exceptions, quality = validate(raw)
    with sqlite3.connect(out/'finguard.db') as conn:
        clean.to_sql('clean_transactions',conn,if_exists='replace',index=False)
        exceptions.to_sql('exceptions',conn,if_exists='replace',index=False)
        quality.to_sql('quality_results',conn,if_exists='replace',index=False)
        risk = pd.read_sql_query((ROOT/'sql'/'local_risk.sql').read_text(),conn)
        risk.to_sql('risk_transactions',conn,if_exists='replace',index=False)
    for name,frame in [('clean_transactions',clean),('exceptions',exceptions),('quality_results',quality),('risk_transactions',risk)]:
        frame.to_csv(out/f'{name}.csv',index=False)
    metrics = {
        'run_id':str(uuid4()),'processed_at_utc':datetime.now(timezone.utc).isoformat(),
        'rules_version':'1.0','input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'input_rows':len(raw),'accepted_rows':len(clean),'rejected_rows':len(exceptions),
        'acceptance_pct':round(100*len(clean)/len(raw),2) if len(raw) else 0,
        'review_rows':int(risk['risk_status'].eq('Review').sum()),
        'high_value_rows':int(risk['high_value'].sum()),'rapid_activity_rows':int(risk['rapid_activity'].sum()),
        'accepted_amount_inr':int(clean['amount'].sum()),'backend':'SQLite (local)'
    }
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    with (out/'audit_history.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(metrics)+'\n')
    print(json.dumps(metrics,indent=2))
    return metrics

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    run(args.input,args.output)

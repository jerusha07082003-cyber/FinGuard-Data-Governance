import json
import sqlite3
import pandas as pd
import pytest
from finguard.generate import generate
from finguard.quality import validate
from finguard.pipeline import run

@pytest.fixture(scope='module')
def raw(): return generate()

@pytest.fixture(scope='module')
def validated(raw): return validate(raw)

def test_reproducible(raw):
    pd.testing.assert_frame_equal(raw,generate())
    assert len(raw)==10100

def test_row_reconciliation(validated):
    clean, rejects, rules=validated
    assert len(clean)==9800 and len(rejects)==300
    assert len(clean)+len(rejects)==10100
    assert clean.transaction_id.is_unique

def test_known_defects(validated):
    _, rejects, rules=validated
    counts=rules.set_index('rule_id').failed_rows.to_dict()
    assert counts['customer_id']==100
    assert counts['amount']==100
    assert counts['duplicate_id']==100
    assert sum(counts.values())==300
    assert len(rejects)==300

def test_masked_outputs(validated):
    clean,rejects,_=validated
    assert 'email' not in clean and 'email' not in rejects
    assert set(clean.email_masked)=={'***@example.com'}

def test_schema_failure(raw):
    with pytest.raises(ValueError,match='Schema mismatch'): validate(raw.drop(columns='currency'))

def test_invalid_first_duplicate(raw):
    sample=raw.iloc[[500,500]].copy().reset_index(drop=True)
    sample.loc[0,'amount']=-1
    clean,rejects,_=validate(sample)
    assert len(clean)==len(rejects)==1
    assert clean.iloc[0].source_row==2

def test_multiple_rules(raw):
    sample=raw.iloc[[500]].copy()
    sample.loc[:,'currency']='USD'
    sample.loc[:,'amount']=-5
    _,rejects,_=validate(sample)
    assert set(rejects.iloc[0].failed_rules.split('|'))=={'amount','currency'}

def test_standardization(raw):
    sample=raw.iloc[[500]].copy()
    sample.loc[:,'currency']=' inr '
    clean,rejects,_=validate(sample)
    assert len(rejects)==0 and clean.iloc[0].currency=='INR'

def test_pipeline_sql_and_audit(tmp_path,raw):
    p=tmp_path/'input.csv'; raw.to_csv(p,index=False)
    out=tmp_path/'out'; metrics=run(p,out)
    assert metrics['acceptance_pct']==97.03
    assert metrics['high_value_rows']==50
    assert metrics['review_rows']==54
    with sqlite3.connect(out/'finguard.db') as conn:
        burst=pd.read_sql_query("SELECT purchases_60m FROM risk_transactions WHERE customer_id='CUST1001' ORDER BY timestamp",conn)
        assert burst.purchases_60m.tolist()==[1,2,3,4,5]
        assert conn.execute('SELECT COUNT(*) FROM exceptions').fetchone()[0]==300
    assert json.loads((out/'audit_history.jsonl').read_text())['run_id']==metrics['run_id']

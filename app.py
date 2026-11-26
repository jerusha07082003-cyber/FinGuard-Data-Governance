"""Streamlit UI for the latest local pipeline snapshot."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from finguard.pipeline import run

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'outputs'
st.set_page_config(page_title='FinGuard | Governance & Risk',page_icon='🛡️',layout='wide')
if not all((OUT/name).exists() for name in ['metrics.json','risk_transactions.csv','exceptions.csv','quality_results.csv','audit_history.jsonl']):
    run()
with st.sidebar:
    st.title('FinGuard')
    st.caption('DATA GOVERNANCE / DEMO')
    st.info('Synthetic purchases only. Local SQLite analytics. Risk flags are not confirmed fraud.')
    if st.button('Re-run local pipeline',use_container_width=True):
        run()
        st.rerun()
    st.markdown('**Data lineage**  \nSynthetic CSV → Python validation → SQLite SQL → dashboard')
metrics=json.loads((OUT/'metrics.json').read_text())
risk=pd.read_csv(OUT/'risk_transactions.csv')
quality=pd.read_csv(OUT/'quality_results.csv')
exceptions=pd.read_csv(OUT/'exceptions.csv')
st.title('Financial data governance & risk analytics')
st.caption(f"Local run • {metrics['processed_at_utc']} • Rules v{metrics['rules_version']}")
a,b,c,d,e=st.columns(5)
a.metric('Input records',f"{metrics['input_rows']:,}")
b.metric('Accepted',f"{metrics['accepted_rows']:,}")
c.metric('Rejected',f"{metrics['rejected_rows']:,}")
d.metric('Acceptance rate',f"{metrics['acceptance_pct']:.2f}%")
e.metric('Risk review',f"{metrics['review_rows']:,}")
overview, dq, risks, governance = st.tabs(['Overview','Data quality','Risk review','Governance & audit'])
with overview:
    st.subheader('Accepted transaction portfolio')
    left,right=st.columns(2)
    with left:
        st.caption('Accepted purchase value by category (INR)')
        st.bar_chart(risk.groupby('merchant_category')['amount'].sum())
    with right:
        st.caption('Accepted purchases by date (UTC)')
        st.line_chart(risk.assign(day=pd.to_datetime(risk.timestamp).dt.date).groupby('day').size())
    st.caption('Data quality is measured over all input rows; risk analytics use accepted rows only.')
    st.dataframe(risk.drop(columns=['email_masked']).head(100),hide_index=True,use_container_width=True)
with dq:
    st.subheader('Quality rules and exception queue')
    st.bar_chart(quality.set_index('rule_id')['failed_rows'])
    st.dataframe(quality,hide_index=True,use_container_width=True)
    rule=st.selectbox('Filter exceptions by rule',['All']+quality.rule_id.tolist())
    subset=exceptions if rule=='All' else exceptions[exceptions.failed_rules.str.split('|',regex=False).apply(lambda x: rule in x)]
    st.caption(f'{len(subset):,} exception rows. A row may fail multiple rules.')
    st.dataframe(subset,hide_index=True,use_container_width=True)
    st.download_button('Download filtered exceptions',subset.to_csv(index=False),'exceptions.csv','text/csv')
with risks:
    st.subheader('Transaction review queue')
    st.caption('High value: > INR 50,000. Velocity: at least 3 accepted purchases for a customer in a trailing 60-minute window (including current transaction).')
    x,y=st.columns(2)
    x.metric('High-value flags',metrics['high_value_rows']); y.metric('Rapid-activity flags',metrics['rapid_activity_rows'])
    categories=st.multiselect('Merchant categories',sorted(risk.merchant_category.unique()),default=sorted(risk.merchant_category.unique()))
    selection=st.radio('Risk filter',['Review only','High value','Rapid activity','All accepted'],horizontal=True)
    view=risk[risk.merchant_category.isin(categories)]
    if selection=='Review only': view=view[view.risk_status=='Review']
    elif selection=='High value': view=view[view.high_value==1]
    elif selection=='Rapid activity': view=view[view.rapid_activity==1]
    view=view.sort_values(['amount','timestamp'],ascending=[False,True]).drop(columns='email_masked')
    st.caption(f'{len(view):,} matching transactions')
    st.dataframe(view,hide_index=True,use_container_width=True)
    st.download_button('Download review queue',view.to_csv(index=False),'risk_review.csv','text/csv')
with governance:
    st.subheader('Data stewardship & run traceability')
    st.markdown('**Proposed owner:** Financial data product owner. **Proposed steward:** Data quality analyst. **Classification:** synthetic demonstration data. These are documented roles, not enterprise permissions.')
    st.markdown('Raw email is removed from processed outputs. Customer IDs remain pseudonymous; this is not anonymization. Exception rows retain only source references and rule names.')
    st.json(metrics)
    history=pd.read_json(OUT/'audit_history.jsonl',lines=True)
    st.dataframe(history[['run_id','processed_at_utc','input_rows','accepted_rows','rejected_rows','review_rows']],hide_index=True,use_container_width=True)
    st.download_button('Download audit log',(OUT/'audit_history.jsonl').read_bytes(),'audit_history.jsonl','application/x-ndjson')
    st.markdown((ROOT/'docs'/'GOVERNANCE.md').read_text())

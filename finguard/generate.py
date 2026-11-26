"""Create reproducible synthetic purchase transactions and known test defects."""
from datetime import datetime, timedelta
from pathlib import Path
import random
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ['Food', 'Shopping', 'Travel', 'Healthcare', 'Entertainment', 'Groceries']
COLUMNS = ['transaction_id','customer_id','amount','currency','merchant_category','transaction_type','timestamp','email']

def generate(seed=42):
    rng = random.Random(seed)
    start = datetime(2026, 11, 1)
    rows = []
    for i in range(1, 10001):
        customer = rng.randint(1, 1000)
        rows.append(dict(transaction_id=f'TX{i:05d}', customer_id=f'CUST{customer:04d}',
                         amount=rng.randint(100,15000), currency='INR',
                         merchant_category=rng.choice(CATEGORIES), transaction_type='Purchase',
                         timestamp=(start+timedelta(minutes=rng.randint(0,43199))).isoformat(sep=' '),
                         email=f'cust{customer:04d}@example.com'))
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.loc[0:99,'customer_id'] = None
    df.loc[100:199,'amount'] = -500
    df.loc[300:349,'amount'] = 95000
    # Five otherwise valid purchases in a 20-minute window, by a synthetic customer.
    for offset in range(5):
        i = 350 + offset
        df.loc[i, ['customer_id','email','timestamp']] = [
            'CUST1001','cust1001@example.com', (start+timedelta(minutes=offset*5)).isoformat(sep=' ')]
    return pd.concat([df, df.iloc[200:300].copy()], ignore_index=True)

def main():
    dest = ROOT/'data'/'transactions.csv'
    dest.parent.mkdir(exist_ok=True)
    df = generate()
    df.to_csv(dest,index=False)
    print(f'Generated {len(df):,} rows: {dest}')

if __name__ == '__main__':
    main()

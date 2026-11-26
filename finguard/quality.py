"""Deterministic quality rules; keep first occurrence among otherwise valid rows."""
import pandas as pd
from .generate import CATEGORIES, COLUMNS

RULES = {
 'transaction_id': ('Completeness / validity','Transaction ID must match TX followed by five digits'),
 'customer_id': ('Completeness / validity','Customer ID must match CUST followed by four digits'),
 'amount': ('Validity','Purchase amount must be a positive whole rupee value'),
 'currency': ('Validity','Currency must be INR'),
 'category': ('Standardization','Merchant category must belong to the approved list'),
 'type': ('Validity','Only Purchase is supported by this demo'),
 'timestamp': ('Validity','Timestamp must parse as a date/time'),
 'email': ('Validity','Email must be a synthetic example.com address'),
 'customer_email': ('Consistency','Synthetic email identifier must agree with customer ID'),
 'duplicate_id': ('Uniqueness','Retain the first otherwise valid occurrence of a transaction ID'),
}

def validate(raw):
    if set(raw.columns) != set(COLUMNS):
        raise ValueError(f'Schema mismatch: expected {COLUMNS}; got {list(raw.columns)}')
    df = raw[COLUMNS].copy().reset_index(drop=True)
    df.insert(0,'source_row',df.index+1)
    # Normalize strings, preserve missing values as pandas NA.
    for col in ['transaction_id','customer_id','currency','merchant_category','transaction_type','email']:
        df[col] = df[col].astype('string').str.strip().replace('',pd.NA)
    df['currency'] = df['currency'].str.upper()
    df['merchant_category'] = df['merchant_category'].str.title()
    df['transaction_type'] = df['transaction_type'].str.title()
    df['email'] = df['email'].str.lower()
    amount = pd.to_numeric(df['amount'],errors='coerce')
    time = pd.to_datetime(df['timestamp'],errors='coerce',utc=True)
    valid_customer = df['customer_id'].str.fullmatch(r'CUST\d{4}',na=False)
    expected_email = df['customer_id'].str.lower()+'@example.com'
    checks = pd.DataFrame({
        'transaction_id': ~df['transaction_id'].str.fullmatch(r'TX\d{5}',na=False),
        'customer_id': ~valid_customer,
        'amount': ~(amount.gt(0)&amount.mod(1).eq(0)&amount.lt(10**12)),
        'currency': ~df['currency'].eq('INR').fillna(False),
        'category': ~df['merchant_category'].isin(CATEGORIES),
        'type': ~df['transaction_type'].eq('Purchase').fillna(False),
        'timestamp': time.isna(),
        'email': ~df['email'].str.fullmatch(r'cust\d{4}@example\.com',na=False),
        'customer_email': valid_customer & ~df['email'].eq(expected_email).fillna(False),
    }).fillna(True).astype(bool)
    eligible = ~checks.any(axis=1)
    checks['duplicate_id'] = False
    checks.loc[eligible,'duplicate_id'] = df.loc[eligible,'transaction_id'].duplicated(keep='first').to_numpy()
    rejected = checks.any(axis=1)
    # Suppress the original address completely in all processed outputs.
    # This is masking, not anonymization; customer identifiers remain.
    df['email_masked'] = '***@example.com'
    df.loc[checks['email'],'email_masked'] = '[redacted]'
    df = df.drop(columns='email')
    df['amount'] = amount
    df['timestamp'] = time.dt.strftime('%Y-%m-%d %H:%M:%S')
    clean = df.loc[~rejected].copy()
    clean['amount'] = clean['amount'].astype('int64')
    # Exception output intentionally contains only row references and rule names.
    exceptions = pd.DataFrame({'source_row':df.loc[rejected,'source_row'],
                               'transaction_id':df.loc[rejected,'transaction_id'],
                               'failed_rules': pd.Series(['|'.join(checks.columns[row]) for row in checks.loc[rejected].to_numpy()],index=checks.index[rejected],dtype='string')})
    results = pd.DataFrame([{'rule_id':k,'dimension':RULES[k][0],'description':RULES[k][1],
                             'failed_rows':int(checks[k].sum()),'evaluated_rows':int(eligible.sum()) if k=='duplicate_id' else len(df)}
                            for k in RULES])
    return clean.reset_index(drop=True),exceptions.reset_index(drop=True),results

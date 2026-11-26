-- BigQuery Standard SQL: review flags, not fraud predictions.
WITH velocity AS (
  SELECT *, COUNT(*) OVER (
    PARTITION BY customer_id ORDER BY UNIX_SECONDS(timestamp)
    RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
  ) AS purchases_60m
  FROM `YOUR_PROJECT_ID.finguard.clean_transactions`
)
SELECT *, amount > 50000 AS high_value, purchases_60m >= 3 AS rapid_activity,
       IF(amount > 50000 OR purchases_60m >= 3,'Review','Routine') AS risk_status
FROM velocity
ORDER BY timestamp, transaction_id;

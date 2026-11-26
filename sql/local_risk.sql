-- SQLite: count accepted purchases in the preceding 60 minutes (including current row).
-- Window peers at the same timestamp are included. Flags are not fraud labels.
WITH velocity AS (
  SELECT *, COUNT(*) OVER (
    PARTITION BY customer_id ORDER BY CAST(strftime('%s', timestamp) AS INTEGER)
    RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
  ) AS purchases_60m
  FROM clean_transactions
)
SELECT *, CASE WHEN amount > 50000 THEN 1 ELSE 0 END AS high_value,
          CASE WHEN purchases_60m >= 3 THEN 1 ELSE 0 END AS rapid_activity,
          CASE WHEN amount > 50000 OR purchases_60m >= 3 THEN 'Review' ELSE 'Routine' END AS risk_status
FROM velocity;

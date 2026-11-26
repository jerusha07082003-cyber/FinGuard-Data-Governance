-- Replace YOUR_PROJECT_ID with your GCP project ID. Dataset: finguard.
SELECT dimension, rule_id, failed_rows, evaluated_rows,
       ROUND(100 * SAFE_DIVIDE(evaluated_rows-failed_rows,evaluated_rows),2) AS pass_pct
FROM `YOUR_PROJECT_ID.finguard.quality_results`
ORDER BY failed_rows DESC, rule_id;

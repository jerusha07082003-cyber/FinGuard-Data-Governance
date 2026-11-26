-- Join rule definitions to exploded exception reasons, and verify rule counts.
WITH exploded AS (
 SELECT rule_id, COUNT(*) AS observed_failures
 FROM `YOUR_PROJECT_ID.finguard.exceptions`, UNNEST(SPLIT(failed_rules,'|')) AS rule_id
 GROUP BY rule_id
)
SELECT q.rule_id,q.failed_rows,COALESCE(e.observed_failures,0) AS observed_failures,
       q.failed_rows=COALESCE(e.observed_failures,0) AS reconciled
FROM `YOUR_PROJECT_ID.finguard.quality_results` q
LEFT JOIN exploded e USING(rule_id)
ORDER BY q.rule_id;

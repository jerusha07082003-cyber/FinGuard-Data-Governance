-- Aggregation + rank: compare category volumes and purchase values.
WITH category_summary AS (
 SELECT merchant_category, COUNT(*) AS purchases, SUM(amount) AS total_inr,
        ROUND(AVG(amount),2) AS average_inr
 FROM `YOUR_PROJECT_ID.finguard.clean_transactions`
 GROUP BY merchant_category
)
SELECT *, DENSE_RANK() OVER(ORDER BY total_inr DESC) AS value_rank
FROM category_summary ORDER BY value_rank;

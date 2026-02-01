-- KPI: Billing Status Breakdown (Count + Amount)
SELECT
  billing_status,
  COUNT(*) AS bill_count,
  ROUND(SUM(amount), 2) AS total_amount
FROM curated_fact_billing
GROUP BY billing_status
ORDER BY bill_count DESC;
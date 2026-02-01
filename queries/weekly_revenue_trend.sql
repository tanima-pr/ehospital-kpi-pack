-- KPI: Weekly Revenue Trend
SELECT
  YEARWEEK(billing_date, 1) AS year_week,
  ROUND(SUM(amount), 2) AS total_revenue
FROM curated_fact_billing
GROUP BY YEARWEEK(billing_date, 1)
ORDER BY year_week;
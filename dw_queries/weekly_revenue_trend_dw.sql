SELECT
  year_week,
  ROUND(SUM(amount), 2) AS total_revenue
FROM EHOSPITAL_DW.fact_billing
WHERE amount IS NOT NULL
GROUP BY year_week
ORDER BY year_week;
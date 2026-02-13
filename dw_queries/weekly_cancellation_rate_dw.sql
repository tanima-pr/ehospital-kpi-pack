SELECT
  year_week,
  ROUND(100 * AVG(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END), 2) AS cancellation_rate_pct
FROM EHOSPITAL_DW.fact_appointments
GROUP BY year_week
ORDER BY year_week;
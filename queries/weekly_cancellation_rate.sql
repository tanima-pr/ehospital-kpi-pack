-- KPI: Weekly Cancellation Rate
SELECT
  YEARWEEK(appointment_dt, 1) AS year_week,
  COUNT(*) AS total_appointments,
  SUM(status = 'Cancelled') AS cancelled_appointments,
  ROUND(SUM(status = 'Cancelled') / COUNT(*) * 100, 2) AS cancel_rate_pct
FROM curated_fact_appointments
GROUP BY YEARWEEK(appointment_dt, 1)
ORDER BY year_week;
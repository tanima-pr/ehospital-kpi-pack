-- KPI: Weekly Appointment Volume
SELECT
  YEARWEEK(appointment_dt, 1) AS year_week,
  COUNT(*) AS appointments
FROM curated_fact_appointments
GROUP BY YEARWEEK(appointment_dt, 1)
ORDER BY year_week;
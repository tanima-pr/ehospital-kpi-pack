SELECT
  year_week,
  COUNT(*) AS appointments
FROM EHOSPITAL_DW.fact_appointments
GROUP BY year_week
ORDER BY year_week;
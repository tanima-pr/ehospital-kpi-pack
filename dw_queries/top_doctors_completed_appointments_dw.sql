SELECT
  doctor_id,
  COUNT(*) AS completed_appointments
FROM EHOSPITAL_DW.fact_appointments
WHERE status = 'Completed'
GROUP BY doctor_id
ORDER BY completed_appointments DESC
LIMIT 10;
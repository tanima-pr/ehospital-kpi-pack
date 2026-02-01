-- KPI: Top Doctors by Completed Appointments
SELECT
  doctor_id,
  COUNT(*) AS completed_appointments
FROM curated_fact_appointments
WHERE status = 'Completed'
GROUP BY doctor_id
ORDER BY completed_appointments DESC
LIMIT 10;
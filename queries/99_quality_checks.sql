-- Curated appointments sanity
SELECT COUNT(*) AS total_rows FROM curated_fact_appointments;
SELECT SUM(appointment_dt IS NULL) AS null_dt FROM curated_fact_appointments;

-- Duplicate appointment IDs
SELECT appointment_id, COUNT(*) c
FROM curated_fact_appointments
GROUP BY appointment_id
HAVING c > 1;

-- Bloodtests sanity
SELECT COUNT(*) AS total_rows FROM curated_fact_bloodtests;
SELECT SUM(test_date IS NULL) AS null_test_date FROM curated_fact_bloodtests;

-- Patient dim sanity
SELECT COUNT(*) AS total_rows FROM curated_dim_patient;
SELECT SUM(patient_id IS NULL) AS null_patient_id FROM curated_dim_patient;
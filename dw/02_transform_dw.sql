USE EHOSPITAL_DW;

-- DIM PATIENT
TRUNCATE TABLE dim_patient;
INSERT INTO dim_patient (
  patient_id, name, dob, gender, phone_number, OHIP_code,
  private_insurance_name, private_insurance_id, weight_kg, height_cm, family_doctor_id
)
SELECT
  patient_id, name, dob, gender, phone_number, OHIP_code,
  private_insurance_name, private_insurance_id, weight_kg, height_cm, family_doctor_id
FROM stg_patients_registration
WHERE patient_id IS NOT NULL;

-- FACT APPOINTMENTS
TRUNCATE TABLE fact_appointments;
INSERT INTO fact_appointments (
  appointment_id, patient_id, doctor_id, appointment_dt, status, year_week
)
SELECT
  appointment_id,
  patient_id,
  doctor_id,
  `datetime` AS appointment_dt,
  status,
  YEARWEEK(`datetime`, 1) AS year_week
FROM stg_appointments
WHERE appointment_id IS NOT NULL
  AND patient_id IS NOT NULL
  AND `datetime` IS NOT NULL;

-- FACT BILLING (might need column name adjustment)
TRUNCATE TABLE fact_billing;
INSERT INTO fact_billing (
  billing_id, appointment_id, patient_id, amount, billing_date, billing_status, bill_type, year_week
)
SELECT
  billing_id,
  appointment_id,
  patient_id,
  amount,
  billing_date,
  status AS billing_status,
  bill_type,
  YEARWEEK(billing_date, 1) AS year_week
FROM stg_billing_records
WHERE billing_id IS NOT NULL
  AND patient_id IS NOT NULL
  AND billing_date IS NOT NULL;

-- FACT BLOODTESTS
TRUNCATE TABLE fact_bloodtests;
INSERT INTO fact_bloodtests (
  patient_id, test_name, result_value, unit, normal_range, test_date, year_week
)
SELECT
  patient_id,
  test_name,
  result_value,
  unit,
  normal_range,
  test_date,
  YEARWEEK(test_date, 1) AS year_week
FROM stg_bloodtests
WHERE patient_id IS NOT NULL
  AND test_name IS NOT NULL
  AND test_date IS NOT NULL;
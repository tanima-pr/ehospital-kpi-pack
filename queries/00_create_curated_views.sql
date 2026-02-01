-- Curated Fact: Appointments
CREATE OR REPLACE VIEW curated_fact_appointments AS
SELECT
  appointment_id,
  patient_id,
  doctor_id,
  `datetime` AS appointment_dt,
  status
FROM appointments
WHERE appointment_id IS NOT NULL
  AND patient_id IS NOT NULL
  AND `datetime` IS NOT NULL;

-- Curated Fact: Bloodtests
CREATE OR REPLACE VIEW curated_fact_bloodtests AS
SELECT
  patient_id,
  test_name,
  result_value,
  unit,
  normal_range,
  test_date
FROM bloodtests
WHERE patient_id IS NOT NULL
  AND test_name IS NOT NULL
  AND test_date IS NOT NULL;

-- Curated Dim: Patient
CREATE OR REPLACE VIEW curated_dim_patient AS
SELECT
  patient_id,
  name,
  dob,
  gender,
  phone_number,
  OHIP_code,
  private_insurance_name,
  private_insurance_id,
  weight_kg,
  height_cm,
  family_doctor_id
FROM patients_registration
WHERE patient_id IS NOT NULL;

-- Curated Fact: Billing (if you made this view)
-- Uncomment and adjust if needed
-- CREATE OR REPLACE VIEW curated_fact_billing AS
-- SELECT ...
-- FROM billing_records
-- WHERE ...;
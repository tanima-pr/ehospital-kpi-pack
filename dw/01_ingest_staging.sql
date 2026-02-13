USE EHOSPITAL_DW;

TRUNCATE TABLE stg_appointments;
INSERT INTO stg_appointments SELECT * FROM DEV01.appointments;

TRUNCATE TABLE stg_billing_records;
INSERT INTO stg_billing_records SELECT * FROM DEV01.billing_records;

TRUNCATE TABLE stg_bloodtests;
INSERT INTO stg_bloodtests SELECT * FROM DEV01.bloodtests;

TRUNCATE TABLE stg_patients_registration;
INSERT INTO stg_patients_registration SELECT * FROM DEV01.patients_registration;
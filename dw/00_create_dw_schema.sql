CREATE DATABASE IF NOT EXISTS EHOSPITAL_DW;
USE EHOSPITAL_DW;

-- Staging tables (raw copy from DEV01)
CREATE TABLE IF NOT EXISTS stg_appointments LIKE DEV01.appointments;
CREATE TABLE IF NOT EXISTS stg_billing_records LIKE DEV01.billing_records;
CREATE TABLE IF NOT EXISTS stg_bloodtests LIKE DEV01.bloodtests;
CREATE TABLE IF NOT EXISTS stg_patients_registration LIKE DEV01.patients_registration;

-- Warehouse tables
CREATE TABLE IF NOT EXISTS dim_patient (
  patient_id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  dob DATE,
  gender VARCHAR(50),
  phone_number VARCHAR(50),
  OHIP_code VARCHAR(50),
  private_insurance_name VARCHAR(255),
  private_insurance_id VARCHAR(255),
  weight_kg DECIMAL(10,2),
  height_cm DECIMAL(10,2),
  family_doctor_id BIGINT,
  loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_appointments (
  appointment_id BIGINT PRIMARY KEY,
  patient_id BIGINT NOT NULL,
  doctor_id BIGINT,
  appointment_dt DATETIME NOT NULL,
  status VARCHAR(100),
  year_week INT,
  loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_fa_patient (patient_id),
  INDEX idx_fa_yearweek (year_week)
);

CREATE TABLE IF NOT EXISTS fact_billing (
  billing_id BIGINT PRIMARY KEY,
  appointment_id BIGINT,
  patient_id BIGINT NOT NULL,
  amount DECIMAL(12,2),
  billing_date DATE NOT NULL,
  billing_status VARCHAR(100),
  bill_type VARCHAR(100),
  year_week INT,
  loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_fb_patient (patient_id),
  INDEX idx_fb_yearweek (year_week)
);

CREATE TABLE IF NOT EXISTS fact_bloodtests (
  bloodtest_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  patient_id BIGINT NOT NULL,
  test_name VARCHAR(255) NOT NULL,
  result_value VARCHAR(255),
  unit VARCHAR(50),
  normal_range VARCHAR(255),
  test_date DATE NOT NULL,
  year_week INT,
  loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_fbt_patient (patient_id),
  INDEX idx_fbt_yearweek (year_week)
);
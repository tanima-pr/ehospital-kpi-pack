"""
knowledge_base.py — the governed "single source of truth" the AI is allowed to use.

This is the heart of the whole project. The AI never guesses what a hospital metric
means — it is GROUNDED in these definitions, taken straight from your eHospital KPI
pack (queries/*.sql). Change a definition here and every answer follows the new rule.

Three kinds of chunks:
  - schema      : which tables/columns exist
  - definition  : how each KPI is calculated (revenue, cancellation rate, ...)
  - example     : a plain-English question paired with the correct SQL
"""

KNOWLEDGE = [
    # ---------------- SCHEMA ----------------
    {"type": "schema", "text":
     "Table dim_patient(patient_id INTEGER PK, name, dob, gender, phone_number, "
     "OHIP_code, private_insurance_name, private_insurance_id, weight_kg, height_cm, "
     "family_doctor_id). One row per patient."},
    {"type": "schema", "text":
     "Table fact_appointments(appointment_id INTEGER PK, patient_id, doctor_id, "
     "appointment_dt TEXT datetime, status, year_week INTEGER). status is one of "
     "'Completed','Cancelled','No-Show','Scheduled'. year_week is a stored YYYYWW bucket."},
    {"type": "schema", "text":
     "Table fact_billing(billing_id INTEGER PK, appointment_id, patient_id, amount REAL, "
     "billing_date DATE, billing_status, bill_type, year_week INTEGER). billing_status is "
     "one of 'Paid','Pending','Denied'. bill_type is one of "
     "'Consultation','Procedure','Lab','Imaging'."},
    {"type": "schema", "text":
     "Table fact_bloodtests(bloodtest_id INTEGER PK, patient_id, test_name, result_value, "
     "unit, normal_range, test_date DATE, year_week INTEGER). One row per blood test performed."},
    {"type": "schema", "text":
     "Joins: fact_billing.patient_id = dim_patient.patient_id. "
     "fact_appointments.patient_id = dim_patient.patient_id. "
     "fact_billing.appointment_id = fact_appointments.appointment_id."},

    # ---------------- DEFINITIONS (KPIs) ----------------
    {"type": "definition", "text":
     "REVENUE = SUM(fact_billing.amount). Weekly revenue trend groups by year_week. "
     "Only fact_billing has money; appointments do not carry amounts."},
    {"type": "definition", "text":
     "APPOINTMENT VOLUME = COUNT(*) of fact_appointments. Weekly volume groups by year_week."},
    {"type": "definition", "text":
     "CANCELLATION RATE (%) = SUM(status = 'Cancelled') / COUNT(*) * 100 over "
     "fact_appointments. Compute per week by grouping on year_week."},
    {"type": "definition", "text":
     "NO-SHOW RATE (%) = SUM(status = 'No-Show') / COUNT(*) * 100 over fact_appointments."},
    {"type": "definition", "text":
     "COMPLETED APPOINTMENTS = COUNT(*) where status = 'Completed'. "
     "Top doctors = group by doctor_id, order by completed count descending."},
    {"type": "definition", "text":
     "INSURANCE TYPE is derived from dim_patient: 'OHIP' when OHIP_code is not null/empty; "
     "else 'Private' when private_insurance_id is not null/empty; else 'Unknown'. "
     "Bill an OHIP-vs-Private split by joining fact_billing to dim_patient."},
    {"type": "definition", "text":
     "BILLING STATUS BREAKDOWN = group fact_billing by billing_status, reporting COUNT(*) "
     "and SUM(amount). Denied or Pending bills flag revenue at risk."},
    {"type": "definition", "text":
     "BLOOD TEST VOLUME = COUNT(*) of fact_bloodtests. Most common tests = group by "
     "test_name, order by count descending. Weekly volume groups by year_week."},

    # ---------------- EXAMPLES (question -> correct SQL) ----------------
    {"type": "example", "text":
     "Q: weekly appointment volume\n"
     "SQL: SELECT year_week, COUNT(*) AS appointments FROM fact_appointments "
     "GROUP BY year_week ORDER BY year_week;"},
    {"type": "example", "text":
     "Q: weekly cancellation rate\n"
     "SQL: SELECT year_week, COUNT(*) AS total_appointments, "
     "SUM(status = 'Cancelled') AS cancelled, "
     "ROUND(SUM(status = 'Cancelled') * 100.0 / COUNT(*), 2) AS cancel_rate_pct "
     "FROM fact_appointments GROUP BY year_week ORDER BY year_week;"},
    {"type": "example", "text":
     "Q: weekly revenue trend\n"
     "SQL: SELECT year_week, ROUND(SUM(amount), 2) AS total_revenue FROM fact_billing "
     "GROUP BY year_week ORDER BY year_week;"},
    {"type": "example", "text":
     "Q: billing split by insurance type (OHIP vs Private)\n"
     "SQL: SELECT CASE WHEN p.OHIP_code IS NOT NULL AND p.OHIP_code <> '' THEN 'OHIP' "
     "WHEN p.private_insurance_id IS NOT NULL AND p.private_insurance_id <> '' THEN 'Private' "
     "ELSE 'Unknown' END AS insurance_type, COUNT(*) AS bills, "
     "ROUND(SUM(b.amount), 2) AS total_amount "
     "FROM fact_billing b JOIN dim_patient p ON p.patient_id = b.patient_id "
     "GROUP BY insurance_type ORDER BY total_amount DESC;"},
    {"type": "example", "text":
     "Q: top doctors by completed appointments\n"
     "SQL: SELECT doctor_id, COUNT(*) AS completed_appointments FROM fact_appointments "
     "WHERE status = 'Completed' GROUP BY doctor_id ORDER BY completed_appointments DESC LIMIT 10;"},
    {"type": "example", "text":
     "Q: most common blood tests\n"
     "SQL: SELECT test_name, COUNT(*) AS test_count FROM fact_bloodtests "
     "GROUP BY test_name ORDER BY test_count DESC LIMIT 10;"},
    {"type": "example", "text":
     "Q: billing status breakdown\n"
     "SQL: SELECT billing_status, COUNT(*) AS bill_count, ROUND(SUM(amount), 2) AS total_amount "
     "FROM fact_billing GROUP BY billing_status ORDER BY bill_count DESC;"},
]

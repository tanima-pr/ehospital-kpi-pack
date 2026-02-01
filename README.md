# eHospital KPI Pack (MySQL)

This repo contains a set of MySQL KPI queries and curated views for an eHospital dataset.

## Folder structure
- `queries/`
  - `00_create_curated_views.sql` → creates curated views used by KPIs
  - `99_quality_checks.sql` → sanity checks / data quality checks
  - `weekly_appointment_volume.sql`
  - `weekly_cancellation_rate.sql`
  - `weekly_blood_tests_volume.sql`
  - `weekly_revenue_trend.sql`
  - `billing_status_breakdown.sql`
  - `billing_by_insurance_type.sql`
  - `top_doctors_completed_appointments.sql`
  - `top_blood_tests.sql`
- `RUNBOOK.md` → step-by-step run order

## How to run (MySQL Workbench)
1. Open MySQL Workbench and select schema `DEV01`
2. Run `queries/00_create_curated_views.sql`
3. Run any KPI query from `queries/` (one file at a time)
4. Run `queries/99_quality_checks.sql` to validate data sanity

## Notes
- Views are created using `CREATE OR REPLACE VIEW`
- KPIs are written to be readable and reusable
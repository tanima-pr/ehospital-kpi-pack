# eHospital KPI Pack — AI-Assisted Healthcare Analytics Workspace

A Proof of Concept analytics workspace built to demonstrate how 
AI-assisted natural-language querying can make hospital operational 
and billing data accessible without requiring SQL expertise.

## Business Problem

Hospital operations teams couldn't easily explore performance data 
without engineering support. This workspace makes KPI data self-serve, 
repeatable, and ready to feed into AI-assisted query interfaces — 
enabling non-technical stakeholders to ask questions in plain language 
and receive data-backed answers.

## What This Repo Contains

The **data layer** of the workspace: curated MySQL views and a reusable 
KPI query library covering:

- Appointment volume and cancellation trends
- Revenue trends and billing breakdowns by insurance type
- Provider performance (top doctors by completed appointments)
- Blood test utilization
- Data quality checks and sanity validation

This structured, governed data layer is designed to be queried directly 
or surfaced through an AI natural-language interface.

## Folder Structure

- `queries/`
  - `00_create_curated_views.sql` → curated views used by all KPIs
  - `99_quality_checks.sql` → data quality and sanity checks
  - `weekly_appointment_volume.sql`
  - `weekly_cancellation_rate.sql`
  - `weekly_blood_tests_volume.sql`
  - `weekly_revenue_trend.sql`
  - `billing_status_breakdown.sql`
  - `billing_by_insurance_type.sql`
  - `top_doctors_completed_appointments.sql`
  - `top_blood_tests.sql`
- `dw/` → data warehouse schema
- `dw_queries/` → warehouse-level queries
- `RUNBOOK.md` → step-by-step run order

## How to Run

1. Open MySQL Workbench and select schema `DEV01`
2. Run `queries/00_create_curated_views.sql`
3. Run any KPI query from `queries/`
4. Run `queries/99_quality_checks.sql` to validate data quality

## Tech Stack

- MySQL (views, KPI queries, data quality checks)
- Structured for AI/LLM query integration over governed data

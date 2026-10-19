-- Migration check: Snowflake output must match the DuckDB baseline exactly. Every row should say MATCH.
with actual as (
    select 'stg_patients' as model, count(*) as row_count from EHOSPITAL.ANALYTICS.STG_PATIENTS
    union all select 'stg_appointments', count(*) from EHOSPITAL.ANALYTICS.STG_APPOINTMENTS
    union all select 'stg_billing',      count(*) from EHOSPITAL.ANALYTICS.STG_BILLING
    union all select 'stg_bloodtests',   count(*) from EHOSPITAL.ANALYTICS.STG_BLOODTESTS
    union all select 'kpi_weekly_appointment_volume', count(*) from EHOSPITAL.ANALYTICS.KPI_WEEKLY_APPOINTMENT_VOLUME
    union all select 'kpi_weekly_cancellation_rate',  count(*) from EHOSPITAL.ANALYTICS.KPI_WEEKLY_CANCELLATION_RATE
    union all select 'kpi_weekly_revenue',            count(*) from EHOSPITAL.ANALYTICS.KPI_WEEKLY_REVENUE
    union all select 'kpi_top_doctors',               count(*) from EHOSPITAL.ANALYTICS.KPI_TOP_DOCTORS
    union all select 'kpi_top_bloodtests',            count(*) from EHOSPITAL.ANALYTICS.KPI_TOP_BLOODTESTS
    union all select 'kpi_billing_by_insurance',      count(*) from EHOSPITAL.ANALYTICS.KPI_BILLING_BY_INSURANCE
    union all select 'total_revenue_x100', round(sum(total_revenue) * 100) from EHOSPITAL.ANALYTICS.KPI_WEEKLY_REVENUE
),
expected (model, row_count) as (
    select * from values
      ('stg_patients', 200), ('stg_appointments', 2000), ('stg_billing', 1218),
      ('stg_bloodtests', 1500), ('kpi_weekly_appointment_volume', 26),
      ('kpi_weekly_cancellation_rate', 26), ('kpi_weekly_revenue', 27),
      ('kpi_top_doctors', 10), ('kpi_top_bloodtests', 8),
      ('kpi_billing_by_insurance', 2), ('total_revenue_x100', 32880394)
)
select e.model, e.row_count as duckdb_baseline, a.row_count as snowflake,
       iff(e.row_count = a.row_count, 'MATCH', 'MISMATCH') as result
from expected e left join actual a using (model)
order by result desc, e.model;

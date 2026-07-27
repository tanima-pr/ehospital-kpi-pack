-- Staging: clean billing records + weekly grain for revenue trends.
with source as (
    select * from {{ ref('raw_billing') }}
)
select
    cast(billing_id as integer)      as billing_id,
    cast(appointment_id as integer)  as appointment_id,
    cast(patient_id as integer)      as patient_id,
    cast(amount as double)           as amount,
    cast(billing_date as date)       as billing_date,
    cast(date_trunc('week', cast(billing_date as timestamp)) as date) as billing_week,
    billing_status,
    bill_type
from source

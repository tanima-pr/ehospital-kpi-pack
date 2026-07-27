-- Staging: clean appointments + add reusable date grains (day + week).
-- date_trunc('week', ...) buckets each appointment into its Monday-based week —
-- the modern, readable replacement for the old YEARWEEK() integer.
with source as (
    select * from {{ ref('raw_appointments') }}
)
select
    cast(appointment_id as integer)         as appointment_id,
    cast(patient_id as integer)             as patient_id,
    cast(doctor_id as integer)              as doctor_id,
    cast(appointment_dt as timestamp)       as appointment_at,
    cast(appointment_dt as date)            as appointment_date,
    cast(date_trunc('week', cast(appointment_dt as timestamp)) as date) as appointment_week,
    status
from source

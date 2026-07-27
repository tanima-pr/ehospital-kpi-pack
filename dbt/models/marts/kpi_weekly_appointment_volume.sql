-- KPI: how many appointments per week.
select
    appointment_week,
    count(*) as appointments
from {{ ref('stg_appointments') }}
group by appointment_week
order by appointment_week

-- KPI: top 10 doctors by number of completed appointments.
select
    doctor_id,
    count(*) as completed_appointments
from {{ ref('stg_appointments') }}
where status = 'Completed'
group by doctor_id
order by completed_appointments desc
limit 10

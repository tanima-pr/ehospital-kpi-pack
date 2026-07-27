-- KPI: what share of each week's appointments were cancelled.
select
    appointment_week,
    count(*)                                                   as total_appointments,
    sum(case when status = 'Cancelled' then 1 else 0 end)      as cancelled_appointments,
    round(sum(case when status = 'Cancelled' then 1 else 0 end) * 100.0
          / count(*), 2)                                       as cancel_rate_pct
from {{ ref('stg_appointments') }}
group by appointment_week
order by appointment_week

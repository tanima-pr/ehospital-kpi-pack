-- KPI: total billed revenue per week.
select
    billing_week,
    round(sum(amount), 2) as total_revenue
from {{ ref('stg_billing') }}
group by billing_week
order by billing_week

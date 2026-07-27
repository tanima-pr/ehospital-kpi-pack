-- KPI: billing split by insurance type (OHIP vs Private vs Unknown).
-- Joins billing to the patient dimension, reusing the insurance_type rule
-- defined once in stg_patients.
select
    p.insurance_type,
    count(*)              as bills,
    round(sum(b.amount), 2) as total_amount
from {{ ref('stg_billing') }} b
join {{ ref('stg_patients') }} p
    on p.patient_id = b.patient_id
group by p.insurance_type
order by total_amount desc

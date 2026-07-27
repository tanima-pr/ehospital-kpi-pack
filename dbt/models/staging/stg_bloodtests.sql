-- Staging: clean blood tests + weekly grain.
with source as (
    select * from {{ ref('raw_bloodtests') }}
)
select
    cast(bloodtest_id as integer)  as bloodtest_id,
    cast(patient_id as integer)    as patient_id,
    test_name,
    cast(test_date as date)        as test_date,
    cast(date_trunc('week', cast(test_date as timestamp)) as date) as test_week
from source

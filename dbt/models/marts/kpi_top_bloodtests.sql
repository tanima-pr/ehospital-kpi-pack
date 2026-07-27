-- KPI: the 10 most frequently ordered blood tests.
select
    test_name,
    count(*) as test_count
from {{ ref('stg_bloodtests') }}
group by test_name
order by test_count desc
limit 10

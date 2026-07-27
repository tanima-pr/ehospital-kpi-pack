-- Staging: one clean row per patient.
-- Here we DERIVE insurance_type once, so every downstream model agrees on the rule.
with source as (
    select * from {{ ref('raw_patients') }}
)
select
    cast(patient_id as integer)        as patient_id,
    name,
    cast(dob as date)                  as date_of_birth,
    gender,
    ohip_code,
    private_insurance_name,
    private_insurance_id,
    cast(family_doctor_id as integer)  as family_doctor_id,
    case
        when ohip_code is not null and ohip_code <> ''                     then 'OHIP'
        when private_insurance_id is not null and private_insurance_id <> '' then 'Private'
        else 'Unknown'
    end                                as insurance_type
from source

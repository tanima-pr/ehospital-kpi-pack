-- KPI: Billing Summary by Insurance (OHIP vs Private)
SELECT
  CASE
    WHEN p.OHIP_code IS NOT NULL AND p.OHIP_code <> '' THEN 'OHIP'
    WHEN p.private_insurance_id IS NOT NULL AND p.private_insurance_id <> '' THEN 'Private'
    ELSE 'Unknown'
  END AS insurance_type,
  COUNT(*) AS bills,
  ROUND(SUM(b.amount), 2) AS total_amount
FROM curated_fact_billing b
JOIN curated_dim_patient p
  ON p.patient_id = b.patient_id
GROUP BY insurance_type
ORDER BY total_amount DESC;
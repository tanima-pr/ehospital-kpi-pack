SELECT
  billing_status,
  COUNT(*) AS bills
FROM EHOSPITAL_DW.fact_billing
GROUP BY billing_status
ORDER BY bills DESC;
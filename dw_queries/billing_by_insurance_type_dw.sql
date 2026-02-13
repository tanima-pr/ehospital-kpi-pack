SELECT
  COALESCE(bill_type, 'Unknown') AS bill_type,
  ROUND(SUM(amount), 2) AS total_amount,
  COUNT(*) AS bills
FROM EHOSPITAL_DW.fact_billing
GROUP BY bill_type
ORDER BY total_amount DESC;
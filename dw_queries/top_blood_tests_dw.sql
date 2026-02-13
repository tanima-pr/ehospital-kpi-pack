SELECT
  test_name,
  COUNT(*) AS test_count
FROM EHOSPITAL_DW.fact_bloodtests
GROUP BY test_name
ORDER BY test_count DESC
LIMIT 10;
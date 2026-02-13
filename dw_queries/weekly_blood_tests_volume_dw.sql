SELECT
  year_week,
  COUNT(*) AS blood_tests
FROM EHOSPITAL_DW.fact_bloodtests
GROUP BY year_week
ORDER BY year_week;
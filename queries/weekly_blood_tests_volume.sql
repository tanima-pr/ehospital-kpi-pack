-- KPI: Weekly Blood Test Volume
SELECT
  YEARWEEK(test_date, 1) AS year_week,
  COUNT(*) AS tests
FROM curated_fact_bloodtests
GROUP BY YEARWEEK(test_date, 1)
ORDER BY year_week;
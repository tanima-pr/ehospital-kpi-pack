-- KPI: Top 10 Most Common Blood Tests
SELECT
  test_name,
  COUNT(*) AS test_count
FROM curated_fact_bloodtests
GROUP BY test_name
ORDER BY test_count DESC
LIMIT 10;
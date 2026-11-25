-- April 2026 proactive line-increase cohort: identified by the credit_line step between 2026-03 and 2026-04, profiled by tier, then compared with untreated B/C accounts opened before 2026-03 that were also active and current in March (autopay-failure accounts excluded from both arms).
WITH step AS (
  SELECT account_id, prev_line AS old_line, credit_line AS new_line FROM (
    SELECT account_id, month, credit_line,
           LAG(credit_line) OVER (PARTITION BY account_id ORDER BY month) AS prev_line
    FROM monthly_performance)
  WHERE month = '2026-04' AND credit_line > prev_line)
SELECT a.credit_tier, COUNT(*) AS treated,
       ROUND(AVG(old_line)) AS avg_old_line, ROUND(AVG(new_line)) AS avg_new_line,
       ROUND(AVG(new_line / old_line), 2) AS avg_multiple,
       MIN(a.open_month) AS earliest_open, MAX(a.open_month) AS latest_open
FROM step JOIN accounts a USING (account_id)
GROUP BY 1 ORDER BY 1;

WITH step AS (
  SELECT account_id FROM (
    SELECT account_id, month, credit_line,
           LAG(credit_line) OVER (PARTITION BY account_id ORDER BY month) AS prev_line
    FROM monthly_performance)
  WHERE month = '2026-04' AND credit_line > prev_line),
ap_fail AS (
  SELECT DISTINCT account_id FROM monthly_performance
  WHERE autopay_failed = 1 AND month IN ('2026-08','2026-09')),
current_mar AS (
  SELECT account_id FROM monthly_performance
  WHERE month = '2026-03' AND status = 'active' AND dpd_bucket = 0),
pop AS (
  SELECT a.account_id,
         CASE WHEN s.account_id IS NOT NULL THEN 'treated' ELSE 'untreated_peer' END AS arm
  FROM accounts a
  JOIN current_mar USING (account_id)
  LEFT JOIN step s USING (account_id)
  WHERE a.open_month < '2026-03' AND a.credit_tier IN ('B','C')
    AND a.account_id NOT IN (SELECT account_id FROM ap_fail))
SELECT p.month, pop.arm, COUNT(*) AS accounts,
       SUM(p.status = 'active') AS active,
       SUM(p.dpd_bucket >= 30 AND p.status = 'active') AS d30,
       ROUND(100.0 * SUM(p.dpd_bucket >= 30 AND p.status = 'active') / SUM(p.status = 'active'), 2) AS rate_pct,
       ROUND(AVG(CASE WHEN p.status = 'active' THEN p.utilization END), 3)        AS avg_util,
       ROUND(AVG(CASE WHEN p.status = 'active' THEN p.statement_balance END))     AS avg_balance
FROM monthly_performance p
JOIN pop USING (account_id)
WHERE p.month IN ('2026-03','2026-05','2026-07','2026-09','2026-11')
GROUP BY 1, 2
ORDER BY 2, 1;

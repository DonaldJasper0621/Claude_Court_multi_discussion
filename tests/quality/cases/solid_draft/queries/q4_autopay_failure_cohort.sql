-- Autopay failures (PAY-4471): failures by month, the bucket path of every account with a failed debit in Aug or Sep 2026 against autopay-without-failure and no-autopay controls, and remediation sizing (ever 30+, still 60+, charged off, and whether current in July).
SELECT month, SUM(autopay_attempted) AS attempted, SUM(autopay_failed) AS failed,
       ROUND(100.0 * SUM(autopay_failed) / SUM(autopay_attempted), 2) AS fail_pct,
       SUM(CASE WHEN autopay_failed = 1 THEN payment_received END) AS payments_on_failed_rows
FROM monthly_performance
WHERE month BETWEEN '2026-06' AND '2026-11'
GROUP BY 1 ORDER BY 1;

WITH f AS (
  SELECT DISTINCT account_id FROM monthly_performance
  WHERE autopay_failed = 1 AND month IN ('2026-08','2026-09'))
SELECT p.month,
       CASE WHEN f.account_id IS NOT NULL THEN '1_autopay_failed_aug_sep'
            WHEN p.autopay_flag = 1        THEN '2_autopay_no_failure'
            ELSE                                '3_no_autopay' END AS grp,
       SUM(p.status = 'active') AS active,
       SUM(p.dpd_bucket = 30 AND p.status = 'active') AS b30,
       SUM(p.dpd_bucket >= 60 AND p.status = 'active') AS b60_plus,
       SUM(p.dpd_bucket >= 30 AND p.status = 'active') AS d30,
       ROUND(100.0 * SUM(p.dpd_bucket >= 30 AND p.status = 'active') / SUM(p.status = 'active'), 2) AS rate_pct
FROM monthly_performance p
LEFT JOIN f USING (account_id)
WHERE p.month BETWEEN '2026-06' AND '2026-11'
GROUP BY 1, 2
ORDER BY 2, 1;

WITH f AS (
  SELECT DISTINCT account_id FROM monthly_performance
  WHERE autopay_failed = 1 AND month IN ('2026-08','2026-09')),
ev AS (
  SELECT p.account_id,
         MAX(CASE WHEN p.month = '2026-07' AND p.dpd_bucket = 0 THEN 1 ELSE 0 END)                   AS current_jul,
         MAX(CASE WHEN p.month BETWEEN '2026-08' AND '2026-11' AND p.dpd_bucket >= 30 THEN 1 ELSE 0 END) AS ever_30,
         MAX(CASE WHEN p.month = '2026-11' THEN p.dpd_bucket END)                                    AS nov_bucket,
         MAX(CASE WHEN p.month = '2026-11' THEN p.status END)                                        AS nov_status
  FROM monthly_performance p JOIN f USING (account_id)
  GROUP BY 1)
SELECT COUNT(*) AS cohort,
       SUM(current_jul) AS current_in_jul,
       SUM(ever_30) AS ever_30plus_aug_nov,
       SUM(ever_30 = 1 AND current_jul = 1) AS ever_30plus_and_current_jul,
       SUM(nov_bucket >= 60) AS nov_60plus,
       SUM(nov_status = 'charged_off') AS nov_charged_off,
       SUM(nov_status = 'charged_off' AND current_jul = 1) AS charged_off_and_current_jul
FROM ev;

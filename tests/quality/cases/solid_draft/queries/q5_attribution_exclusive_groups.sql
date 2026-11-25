-- Change in 30+ active accounts attributed to mutually exclusive groups (priority: autopay-failed > April CLI > spring campaign > spring organic > post-May vintage > rest of book), shown from a May base, a July base and for the Jul->Sep spike.
WITH f AS (
  SELECT DISTINCT account_id FROM monthly_performance
  WHERE autopay_failed = 1 AND month IN ('2026-08','2026-09')),
cli AS (
  SELECT account_id FROM (
    SELECT account_id, month, credit_line,
           LAG(credit_line) OVER (PARTITION BY account_id ORDER BY month) AS prev_line
    FROM monthly_performance)
  WHERE month = '2026-04' AND credit_line > prev_line),
grp AS (
  SELECT a.account_id,
         CASE WHEN f.account_id IS NOT NULL                        THEN '1_autopay_failed_aug_sep'
              WHEN c.account_id IS NOT NULL                        THEN '2_cli_april_treated'
              WHEN a.campaign_id = 'CMP-2026-SPRING-INSTORE'       THEN '3_spring_campaign_vintage'
              WHEN a.open_month BETWEEN '2026-03' AND '2026-05'    THEN '4_spring_organic_vintage'
              WHEN a.open_month >= '2026-06'                       THEN '5_post_may_vintage'
              ELSE                                                      '6_rest_of_book' END AS g
  FROM accounts a
  LEFT JOIN f USING (account_id)
  LEFT JOIN cli c USING (account_id)),
m AS (
  SELECT g, month,
         SUM(status = 'active') AS active,
         SUM(dpd_bucket >= 30 AND status = 'active') AS d30
  FROM monthly_performance JOIN grp USING (account_id)
  WHERE month IN ('2026-05','2026-07','2026-09','2026-11')
  GROUP BY 1, 2)
SELECT g,
       COUNT(DISTINCT grp.account_id) AS accounts,
       MAX(CASE WHEN month = '2026-05' THEN d30 END) AS may_d30,
       MAX(CASE WHEN month = '2026-07' THEN d30 END) AS jul_d30,
       MAX(CASE WHEN month = '2026-09' THEN d30 END) AS sep_d30,
       MAX(CASE WHEN month = '2026-11' THEN d30 END) AS nov_d30,
       MAX(CASE WHEN month = '2026-11' THEN d30 END) - COALESCE(MAX(CASE WHEN month = '2026-05' THEN d30 END), 0) AS chg_may_nov,
       MAX(CASE WHEN month = '2026-11' THEN d30 END) - MAX(CASE WHEN month = '2026-07' THEN d30 END) AS chg_jul_nov,
       MAX(CASE WHEN month = '2026-09' THEN d30 END) - MAX(CASE WHEN month = '2026-07' THEN d30 END) AS chg_jul_sep,
       ROUND(100.0 * MAX(CASE WHEN month = '2026-05' THEN d30 END) / MAX(CASE WHEN month = '2026-05' THEN active END), 2) AS may_rate_pct,
       ROUND(100.0 * MAX(CASE WHEN month = '2026-11' THEN d30 END) / MAX(CASE WHEN month = '2026-11' THEN active END), 2) AS nov_rate_pct
FROM m JOIN grp USING (g)
GROUP BY 1
ORDER BY 1;

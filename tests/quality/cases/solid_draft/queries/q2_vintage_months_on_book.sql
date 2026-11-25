-- Spring 2026 vintages: size and origination profile by open month, then 30+ (active/active) by months on book versus the Jun-Oct 2025 organic vintage, excluding accounts hit by the Aug/Sep autopay failure or the April line increase so the curves show seasoning only.
SELECT open_month, campaign_id, COUNT(*) AS accounts,
       ROUND(AVG(fico_at_origination), 1) AS avg_fico,
       ROUND(AVG(initial_credit_line))    AS avg_line,
       SUM(credit_tier IN ('C','D'))      AS tier_c_d
FROM accounts
WHERE open_month BETWEEN '2026-01' AND '2026-07'
GROUP BY 1, 2
ORDER BY 1, 2;

WITH ap_fail AS (
  SELECT DISTINCT account_id FROM monthly_performance
  WHERE autopay_failed = 1 AND month IN ('2026-08','2026-09')),
cli AS (
  SELECT account_id FROM (
    SELECT account_id, month, credit_line,
           LAG(credit_line) OVER (PARTITION BY account_id ORDER BY month) AS prev_line
    FROM monthly_performance)
  WHERE month = '2026-04' AND credit_line > prev_line),
v AS (
  SELECT a.account_id,
         CASE WHEN a.campaign_id = 'CMP-2026-SPRING-INSTORE'          THEN 'spring_campaign'
              WHEN a.open_month BETWEEN '2026-03' AND '2026-05'        THEN 'spring_organic'
              WHEN a.open_month BETWEEN '2025-06' AND '2025-10'        THEN 'jun_oct_2025_organic' END AS vintage
  FROM accounts a
  WHERE a.account_id NOT IN (SELECT account_id FROM ap_fail)
    AND a.account_id NOT IN (SELECT account_id FROM cli))
SELECT v.vintage, p.months_on_book,
       SUM(p.status = 'active')                              AS active,
       SUM(p.dpd_bucket >= 30 AND p.status = 'active')       AS d30,
       ROUND(100.0 * SUM(p.dpd_bucket >= 30 AND p.status = 'active') / SUM(p.status = 'active'), 2) AS rate_pct
FROM monthly_performance p
JOIN v USING (account_id)
WHERE v.vintage IS NOT NULL AND p.months_on_book BETWEEN 1 AND 8
GROUP BY 1, 2
ORDER BY 1, 2;

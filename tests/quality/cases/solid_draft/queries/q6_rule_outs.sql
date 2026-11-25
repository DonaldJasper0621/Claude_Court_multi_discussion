-- Rule-outs, one number each: holiday seasonality (Nov-over-Oct change in both years), Texas vs rest, affiliate channel and 2025 holiday campaign, and FICO / tier mix of the active book over time.
SELECT month, dpd30_plus_accounts, dpd30_plus_rate_pct,
       dpd30_plus_accounts - LAG(dpd30_plus_accounts) OVER (ORDER BY month) AS chg_accounts,
       ROUND(dpd30_plus_rate_pct - LAG(dpd30_plus_rate_pct) OVER (ORDER BY month), 2) AS chg_rate_pct
FROM kpi_report_as_published
WHERE month IN ('2025-10','2025-11','2026-10','2026-11')
ORDER BY 1;

SELECT p.month,
       CASE WHEN a.state = 'TX' THEN 'TX' ELSE 'other_states' END AS seg,
       SUM(p.status = 'active') AS active,
       SUM(p.dpd_bucket >= 30 AND p.status = 'active') AS d30,
       ROUND(100.0 * SUM(p.dpd_bucket >= 30 AND p.status = 'active') / SUM(p.status = 'active'), 2) AS rate_pct
FROM monthly_performance p JOIN accounts a USING (account_id)
WHERE p.month IN ('2026-05','2026-09','2026-11')
GROUP BY 1, 2 ORDER BY 2, 1;

SELECT p.month,
       CASE WHEN a.acquisition_channel = 'affiliate' THEN 'affiliate'
            WHEN a.campaign_id = 'CMP-2025-HOLIDAY'  THEN 'holiday_2025_campaign'
            ELSE 'everything_else' END AS seg,
       SUM(p.status = 'active') AS active,
       SUM(p.dpd_bucket >= 30 AND p.status = 'active') AS d30,
       ROUND(100.0 * SUM(p.dpd_bucket >= 30 AND p.status = 'active') / SUM(p.status = 'active'), 2) AS rate_pct
FROM monthly_performance p JOIN accounts a USING (account_id)
WHERE p.month IN ('2026-05','2026-09','2026-11')
GROUP BY 1, 2 ORDER BY 2, 1;

SELECT p.month, COUNT(*) AS active,
       ROUND(AVG(a.fico_at_origination), 1) AS avg_fico_at_orig,
       ROUND(100.0 * SUM(a.credit_tier IN ('C','D')) / COUNT(*), 1) AS pct_tier_c_d
FROM monthly_performance p JOIN accounts a USING (account_id)
WHERE p.status = 'active' AND p.month IN ('2026-02','2026-05','2026-08','2026-11')
GROUP BY 1 ORDER BY 1;

-- Published 30+ DPD series restated on both denominators (v1 = 30+ open / all open; v2 = 30+ active / active), with the published v2 numerator reproduced and the pre-March-2026 book shown separately to isolate the spring denominator effect.
WITH m AS (
  SELECT p.month,
         SUM(p.status IN ('active','open_no_balance'))                                     AS open_all,
         SUM(p.status = 'active')                                                           AS active,
         SUM(p.dpd_bucket >= 30 AND p.status IN ('active','open_no_balance'))              AS d30_open,
         SUM(p.dpd_bucket >= 30 AND p.status = 'active')                                    AS d30_active,
         SUM(a.open_month < '2026-03' AND p.status IN ('active','open_no_balance'))        AS open_pre_mar,
         SUM(a.open_month < '2026-03' AND p.dpd_bucket >= 30
             AND p.status IN ('active','open_no_balance'))                                  AS d30_pre_mar
  FROM monthly_performance p
  JOIN accounts a USING (account_id)
  GROUP BY 1)
SELECT m.month,
       k.dpd30_plus_rate_pct                          AS published_pct,
       k.definition_version                           AS ver,
       k.dpd30_plus_accounts                          AS published_num,
       d30_open, open_all,  ROUND(100.0 * d30_open   / open_all, 2) AS v1_basis_pct,
       d30_active, active,  ROUND(100.0 * d30_active / active,   2) AS v2_basis_pct,
       ROUND(100.0 * d30_open / active, 2)            AS published_recalc_pct,
       d30_pre_mar, open_pre_mar, ROUND(100.0 * d30_pre_mar / open_pre_mar, 2) AS pre_mar_book_v1_pct
FROM m JOIN kpi_report_as_published k USING (month)
WHERE m.month >= '2025-11'
ORDER BY 1;

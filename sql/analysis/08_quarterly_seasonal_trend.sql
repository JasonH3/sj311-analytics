-- Quarterly volume and average resolution time, citywide — the seasonal
-- trend line that ends up on the Tableau dashboard.
--
-- Why join through dim_date instead of strftime() on the raw timestamp:
-- once a date dimension exists, "group by quarter" is a plain join + GROUP
-- BY on an already-computed column, not a date-function call repeated
-- over a million rows in every query that needs it.
SELECT
    dt.year,
    dt.quarter,
    COUNT(*) AS total_requests,
    ROUND(AVG(f.resolution_hours_capped), 1) AS avg_resolution_hours
FROM fact_service_requests f
JOIN dim_date dt ON f.date_created_id = dt.date_id
GROUP BY dt.year, dt.quarter
ORDER BY dt.year, dt.quarter;

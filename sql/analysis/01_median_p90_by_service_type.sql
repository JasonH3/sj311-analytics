-- Median and p90 resolution time by service type.
--
-- Why percentiles instead of AVG: resolution_hours is heavily right-skewed
-- (see the EDA notebook) — a handful of multi-week outliers pull the mean
-- up so much that "average resolution time" misrepresents the typical
-- resident's experience. Percentiles describe the distribution's shape,
-- not just its center.
--
-- Why NTILE(100) instead of PERCENTILE_CONT: SQLite has no native
-- percentile function (Postgres/Oracle do). NTILE is a window function
-- available everywhere, so bucketing rows into 100 equal-sized groups and
-- reading off bucket 50 / 90 gives a portable, if slightly coarse,
-- approximation — exact on large groups, which service-type volumes are.
WITH closed_requests AS (
    SELECT
        dst.service_type_name,
        f.resolution_hours_capped AS hrs
    FROM fact_service_requests f
    JOIN dim_status ds ON f.status_id = ds.status_id
    JOIN dim_service_type dst ON f.service_type_id = dst.service_type_id
    WHERE ds.status_name = 'Closed'
      AND f.is_zero_duration = 0        -- exclude same-instant auto-closures (log #6)
),
ranked AS (
    SELECT
        service_type_name,
        hrs,
        NTILE(100) OVER (PARTITION BY service_type_name ORDER BY hrs) AS pctile_bucket
    FROM closed_requests
)
SELECT
    service_type_name,
    COUNT(*) AS n_closed,
    ROUND(AVG(CASE WHEN pctile_bucket = 50 THEN hrs END), 1) AS median_hours,
    ROUND(AVG(CASE WHEN pctile_bucket = 90 THEN hrs END), 1) AS p90_hours
FROM ranked
GROUP BY service_type_name
ORDER BY p90_hours DESC;

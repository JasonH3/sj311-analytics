-- Top 3 slowest-to-resolve service types within each district, by median
-- resolution time.
--
-- Why RANK() partitioned by district: a flat "slowest service types
-- overall" list would just surface whichever type is slow everywhere and
-- hide district-specific problems — e.g. a type that's fast citywide but
-- unusually slow in one district, which is exactly the kind of finding
-- that should drive a resource-reallocation recommendation.
--
-- Why median (via NTILE) instead of AVG here: same right-skew issue as
-- query 01 — a few weeks-old outliers in a 30-row district/type bucket
-- would swing an average far more than a median.
WITH closed_by_district_type AS (
    SELECT
        dd.district_id,
        dst.service_type_name,
        f.resolution_hours_capped AS hrs
    FROM fact_service_requests f
    JOIN dim_status ds ON f.status_id = ds.status_id
    JOIN dim_service_type dst ON f.service_type_id = dst.service_type_id
    JOIN dim_district dd ON f.district_id = dd.district_id
    WHERE ds.status_name = 'Closed'
      AND f.is_zero_duration = 0
),
bucketed AS (
    SELECT
        district_id,
        service_type_name,
        hrs,
        NTILE(2) OVER (PARTITION BY district_id, service_type_name ORDER BY hrs) AS half
    FROM closed_by_district_type
),
median_by_district_type AS (
    SELECT
        district_id,
        service_type_name,
        COUNT(*) AS n_closed,
        MAX(CASE WHEN half = 1 THEN hrs END) AS median_hours
    FROM bucketed
    GROUP BY district_id, service_type_name
    HAVING COUNT(*) >= 30   -- drop combinations too small for a stable median
),
ranked AS (
    SELECT
        district_id,
        service_type_name,
        n_closed,
        ROUND(median_hours, 1) AS median_hours,
        RANK() OVER (PARTITION BY district_id ORDER BY median_hours DESC) AS slowness_rank
    FROM median_by_district_type
)
SELECT district_id, service_type_name, n_closed, median_hours, slowness_rank
FROM ranked
WHERE slowness_rank <= 3
ORDER BY district_id, slowness_rank;

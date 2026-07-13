-- Year-over-year change in request volume per district — is a district's
-- request load trending up or down, independent of seasonal noise within
-- a year.
--
-- Why LAG() partitioned by district ordered by year (rather than a
-- self-join on year = year - 1): the window function reads naturally as
-- "this year vs. whatever came immediately before it" and doesn't require
-- writing a second copy of the aggregation to join against itself.
WITH yearly_counts AS (
    SELECT
        dd.district_id,
        dt.year,
        COUNT(*) AS request_count
    FROM fact_service_requests f
    JOIN dim_district dd ON f.district_id = dd.district_id
    JOIN dim_date dt ON f.date_created_id = dt.date_id
    GROUP BY dd.district_id, dt.year
)
SELECT
    district_id,
    year,
    request_count,
    LAG(request_count) OVER (PARTITION BY district_id ORDER BY year) AS prior_year_count,
    ROUND(
        100.0 * (request_count - LAG(request_count) OVER (PARTITION BY district_id ORDER BY year))
        / LAG(request_count) OVER (PARTITION BY district_id ORDER BY year),
        1
    ) AS pct_change_yoy
FROM yearly_counts
ORDER BY district_id, year;

-- Month-over-month change in request volume per department.
--
-- Why a CTE to stage monthly aggregates first: LAG() needs one row per
-- (department, month) to compare against the previous month — computing
-- that grouping and the window function in the same SELECT would force
-- recomputing the aggregate for every window frame. Staging it once in
-- monthly_counts keeps the window function's job to exactly one thing:
-- looking at the previous row.
WITH monthly_counts AS (
    SELECT
        dd2.department_name,
        dt.year,
        dt.month,
        COUNT(*) AS request_count
    FROM fact_service_requests f
    JOIN dim_department dd2 ON f.department_id = dd2.department_id
    JOIN dim_date dt ON f.date_created_id = dt.date_id
    GROUP BY dd2.department_name, dt.year, dt.month
)
SELECT
    department_name,
    year,
    month,
    request_count,
    LAG(request_count) OVER (
        PARTITION BY department_name ORDER BY year, month
    ) AS prior_month_count,
    request_count - LAG(request_count) OVER (
        PARTITION BY department_name ORDER BY year, month
    ) AS change_vs_prior_month,
    ROUND(
        100.0 * (request_count - LAG(request_count) OVER (PARTITION BY department_name ORDER BY year, month))
        / LAG(request_count) OVER (PARTITION BY department_name ORDER BY year, month),
        1
    ) AS pct_change_vs_prior_month
FROM monthly_counts
ORDER BY department_name, year, month;

-- Current backlog (Open / In Progress / ReAssigned / Referred) by
-- department, with backlog share of that department's total volume.
--
-- Why backlog share and not just backlog count: a department that
-- receives 100,000 requests a year with 2,000 open is in a very different
-- position than one that receives 3,000 requests with 2,000 open, even
-- though the raw open counts could look similar. This is the metric that
-- should actually drive a "reallocate staff to department X" recommendation.
SELECT
    dep.department_name,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN ds.status_name != 'Closed' THEN 1 ELSE 0 END) AS open_backlog,
    ROUND(
        100.0 * SUM(CASE WHEN ds.status_name != 'Closed' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS pct_open
FROM fact_service_requests f
JOIN dim_status ds ON f.status_id = ds.status_id
JOIN dim_department dep ON f.department_id = dep.department_id
GROUP BY dep.department_name
HAVING COUNT(*) >= 100
ORDER BY pct_open DESC;

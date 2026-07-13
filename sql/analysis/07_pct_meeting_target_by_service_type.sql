-- % of closed requests resolved within a 10-business-day (240 hour) target,
-- by service type. This is the metric a city-manager audience actually
-- cares about — "is the department meeting its response-time target" is a
-- yes/no operational question, where median hours is an analyst's metric.
--
-- 240 hours (10 calendar days) is used as an illustrative target since the
-- dataset doesn't ship official SLA thresholds per type; the README states
-- this assumption explicitly rather than presenting it as an official SLA.
SELECT
    dst.service_type_name,
    COUNT(*) AS n_closed,
    SUM(CASE WHEN f.resolution_hours <= 240 THEN 1 ELSE 0 END) AS n_within_target,
    ROUND(
        100.0 * SUM(CASE WHEN f.resolution_hours <= 240 THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS pct_within_target
FROM fact_service_requests f
JOIN dim_status ds ON f.status_id = ds.status_id
JOIN dim_service_type dst ON f.service_type_id = dst.service_type_id
WHERE ds.status_name = 'Closed'
GROUP BY dst.service_type_name
HAVING COUNT(*) >= 100
ORDER BY pct_within_target ASC;

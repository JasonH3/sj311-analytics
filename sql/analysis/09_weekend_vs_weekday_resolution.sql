-- Weekend vs. weekday submissions: volume share and resolution time.
--
-- Why this matters operationally: if weekend submissions take
-- meaningfully longer to resolve, that's a staffing-schedule finding
-- (fewer staff on duty to triage/dispatch), not a service-type or
-- district finding — a different kind of recommendation than the rest of
-- this analysis surfaces.
SELECT
    CASE WHEN f.is_weekend_submission = 1 THEN 'Weekend' ELSE 'Weekday' END AS submission_period,
    COUNT(*) AS total_requests,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_service_requests), 1) AS pct_of_all_requests,
    ROUND(AVG(f.resolution_hours_capped), 1) AS avg_resolution_hours
FROM fact_service_requests f
JOIN dim_status ds ON f.status_id = ds.status_id
WHERE ds.status_name = 'Closed'
GROUP BY submission_period;

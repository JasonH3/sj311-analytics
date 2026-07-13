-- Resolution time and volume by channel (Self-Service Digital vs.
-- Staff-Assisted vs. Unknown) — sets up the Mann-Whitney U test in Phase 6.
--
-- Why report median AND mean here even though we mostly favor median
-- elsewhere: the *gap* between mean and median is itself informative — a
-- channel with a much higher mean than median is the one being dragged by
-- outliers, which is worth knowing before running a hypothesis test on it.
WITH closed_requests AS (
    SELECT
        f.channel_id,
        f.resolution_hours_capped AS hrs
    FROM fact_service_requests f
    JOIN dim_status ds ON f.status_id = ds.status_id
    WHERE ds.status_name = 'Closed'
      AND f.is_zero_duration = 0
),
ranked AS (
    SELECT
        channel_id,
        hrs,
        NTILE(2) OVER (PARTITION BY channel_id ORDER BY hrs) AS half
    FROM closed_requests
)
SELECT
    dc.channel_name,
    COUNT(*) AS n_closed,
    ROUND(AVG(r.hrs), 1) AS mean_hours,
    ROUND(MAX(CASE WHEN r.half = 1 THEN r.hrs END), 1) AS median_hours_approx
FROM ranked r
JOIN dim_channel dc ON r.channel_id = dc.channel_id
GROUP BY dc.channel_name
ORDER BY median_hours_approx DESC;

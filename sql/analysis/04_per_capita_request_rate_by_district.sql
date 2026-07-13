-- Requests per 1,000 residents by district — the join that the population
-- supplementary dataset exists for.
--
-- Why per-capita and not raw counts: District 3 (downtown) generates far
-- more raw requests than a residential district simply because it has
-- more households and commercial density, not because the city responds
-- differently there. Dividing by population is what makes districts
-- comparable at all; ranking by raw volume would just recreate the
-- population ranking.
SELECT
    dd.district_id,
    dd.council_member,
    dd.population_2020,
    COUNT(*) AS total_requests,
    ROUND(1000.0 * COUNT(*) / dd.population_2020, 1) AS requests_per_1k_residents,
    ROUND(AVG(f.resolution_hours_capped), 1) AS avg_resolution_hours
FROM fact_service_requests f
JOIN dim_district dd ON f.district_id = dd.district_id
GROUP BY dd.district_id, dd.council_member, dd.population_2020
ORDER BY requests_per_1k_residents DESC;

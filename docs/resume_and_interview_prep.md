# Resume Bullets & Interview Prep

## Resume bullets

Pick 2-3 depending on the role (data analyst roles: lead with #1/#3;
data engineering-leaning roles: lead with #1/#2).

1. **Built an end-to-end analytics pipeline on 1.1M+ civic service records** (Python/pandas, SQLite star schema, SQL window functions) to identify response-time bottlenecks for a city 311 system, documenting and resolving 10 distinct data quality issues including a mid-dataset system migration that silently changed the source taxonomy.

2. **Designed a 6-dimension star schema and 10 analytical SQL queries** (CTEs, `RANK`/`LAG`/`NTILE` window functions, multi-table joins) to surface per-district, per-category resolution-time patterns across 4 years of data; added a supplementary geospatial join (Shapely point-in-polygon against council district boundaries) to enable per-capita request-rate analysis.

3. **Applied hypothesis testing and regression (SciPy, statsmodels) to separate real operational drivers from confounded raw metrics** — quantified that weekend-submitted requests take ~219% longer to resolve and that a naive volume-based district ranking would have misdirected resource allocation, informing 4 quantified recommendations delivered via an interactive Tableau Public dashboard.

## Interview prep

**"Walk me through this project."**
Structure the answer as: business question → data source and why it's
messy → the schema design decision (star schema over a flat table, and
why) → the 2-3 headline findings, each with a number → the recommendation
each finding supports → one thing you'd do differently with more time.
Don't lead with tooling ("I used pandas and SQL") — lead with the question
and let the tools come up naturally as you explain how you answered it.

**"Why SQLite instead of Postgres, if the requirement was 'real SQL'?"**
SQLite (3.25+) supports CTEs and window functions fully — nothing about
the analysis is limited by the engine choice. The trade-off was
reproducibility: anyone cloning the repo runs it with zero server setup.
Every query is standard ANSI SQL and would run unmodified against
Postgres. Be ready to say you could migrate it in an afternoon if asked —
and mean it, since the schema/queries genuinely are portable.

**"Why median/percentile instead of average?"**
Resolution time is heavily right-skewed — show the log-histogram if asked.
A handful of multi-week outliers pull the mean up so far it misrepresents
a typical resident's experience. This is also why the regression models
log(resolution_hours) rather than raw hours, and why the hypothesis test
uses Mann-Whitney U rather than a t-test.

**"SQLite doesn't have PERCENTILE_CONT — how did you compute percentiles?"**
`NTILE(100)` as a window function, bucketing rows into 100 equal-sized
groups per partition and reading off bucket 50/90. It's a portable
approximation available on any SQL engine with window function support,
and exact enough on the volumes in this dataset (thousands of rows per
service type) to be reliable.

**"What was the most interesting data quality problem you found?"**
The channel/source taxonomy changed structurally between 2022 and 2023 —
2021-22 requests were logged through "CX Console"/"Web Console," 2023-24
through "Agent desktop"/"Walk-ins." That's not random noise, it's evidence
the city replaced its CRM mid-dataset. Comparing raw Source values across
years would have silently conflated a system change with a real behavior
change — the fix was collapsing 14 raw values into 2 stable channels
(Self-Service Digital / Staff-Assisted) that mean the same thing regardless
of which system logged them.

**"Your regression found District 3 resolves faster than District 1 — but you also said per-capita volume is highest in District 3. Isn't that contradictory?"**
No — it's the point of the model. Raw per-capita volume answers "who
requests the most," which is mostly a population/density question.
Controlling for service-type mix and season answers "who does the city
actually respond to slowly," which is the operational question. They're
different rankings by design; a regression that produced the same ranking
as the raw volume table would have added nothing.

**"Isn't the department-workload coefficient (busier month = faster resolution) a strange finding? How do you know it's not real?"**
It could be partially real, but the honest read is that it's likely
compositional: without department fixed effects, that coefficient can't
distinguish "this department is fast because it's specialized/streamlined
for high-volume categories" from "more volume this month caused faster
resolution." The right follow-up, if I had more time, would be adding
department fixed effects (or an interaction term) to isolate a true
within-department backlog effect — worth saying that's the natural next
step rather than defending the coefficient as-is.

**"What would you do with another week?"**
Two honest answers, pick based on what the interviewer seems to care
about: (1) get GPS/geo coverage above 43% — maybe by geocoding department
+ street-level free text where lat/long is missing, since the map and
district findings only cover the geo-valid subset; (2) add department
fixed effects to the regression to properly separate a within-department
backlog effect from the cross-department compositional effect flagged in
the findings.

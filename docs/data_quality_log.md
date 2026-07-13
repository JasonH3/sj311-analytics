# Data Quality Log — San Jose 311 Service Requests (2021–2024)

Profiled on the combined 4-year dataset (1,123,066 rows, 10 raw columns:
`Incident_ID, Status, Source, Category, Service Type, Latitude, Longitude,
Date Created, Date Last Updated, Department`). Each issue below records what
was found, the decision made, and why — this is the log referenced in the
README methodology section.

| # | Issue | Scope | Decision | Rationale |
|---|-------|-------|----------|-----------|
| 1 | `Category` column is 62.6% null | all years | Drop column; use `Service Type` (20 values, 0.9% null) as the category dimension | `Category` is too sparse to be a reliable grouping key; `Service Type` covers the same concept and is nearly complete |
| 2 | `Department` is 34.8% null | concentrated, not random | Impute from the modal `Department` for each `Service Type` where one exists; else label `Unknown` | Department is largely a function of service type (e.g. "Pothole" → DOT), so a lookup recovers most rows without guessing; residual `Unknown` is kept visible rather than silently dropped |
| 3 | Missing GPS is encoded as `(0, 0)` instead of null | 639,813 rows (57%) | Convert `(0,0)` pairs to `NaN` before any geo aggregation or mapping | `(0,0)` is a real point in the Gulf of Guinea, not San Jose — treating it as a valid coordinate would silently corrupt the district/map analysis. This also means per-capita and per-district metrics only cover ~43% of requests; the README calls this out as a stated limitation rather than hiding it |
| 4 | `Source` (channel) taxonomy changes structurally between 2022 and 2023 | system migration | Map the 14 raw `Source` values into 2 analysis channels: `Self-Service Digital` (VBCS Web, End-User Pages, Web Console, Web, Mobile, Live Chat, Public API, Oracle Integration) vs. `Staff-Assisted` (Agent desktop, CX Console, SFDC-DOT, Walk-ins, Email, Utilities); null → `Unknown` | 2021–22 requests were logged through "CX Console"/"Web Console"; 2023–24 use "Agent desktop"/"Walk-ins" — evidence the city's CRM was replaced mid-dataset. Comparing raw `Source` values across years would conflate a system change with a real behavior change. Collapsing to two stable channels preserves the "self-submitted vs. staff-assisted" comparison the hypothesis test needs, without depending on any one system's naming |
| 5 | `Service Type` contains a garbage value `RGR?CCC` | 13,477 rows, 2024 only (4% of that year) | Recode to `Unknown/Other`; flagged, not guessed | Looks like a truncated/mis-encoded export artifact unique to one year's extract. Its true meaning can't be inferred from the data itself, so it's labeled explicitly rather than mapped to a plausible-looking category, which would fabricate a signal |
| 6 | 18,233 requests have `Date Last Updated == Date Created` (zero-duration) | all years | Flag with `is_zero_duration`; excluded from resolution-time statistics, kept in volume counts | Same-instant open/close likely reflects auto-closed, duplicate, or invalid submissions rather than genuine 0-hour service — including them would bias resolution-time distributions toward zero |
| 7 | 118 requests have resolution time > 2 years (max ~29,761 hours ≈ 3.4 years) | all years | Cap (winsorize) at the 99th percentile for statistical summaries and the regression; raw value retained in a separate column | These are almost certainly stale tickets closed in a bulk cleanup rather than a 3-year service response — left uncapped, a handful of rows would dominate the mean and regression coefficients |
| 8 | `Status` has 5 values; only `Closed` (91.9%) has a meaningful resolution time | all years | Compute `resolution_hours` only for `Closed` rows; `Open`/`In Progress`/`ReAssigned`/`Referred` rows are right-censored (still unresolved) and excluded from resolution-time analysis, but retained for volume/backlog metrics | Treating an open ticket's current age as its "resolution time" would understate true resolution time and bias it downward |
| 9 | No duplicate `Incident_ID` values | all years | No dedup needed | Verified rather than assumed — worth stating explicitly since duplicate tickets were a real risk from a multi-channel intake system |

**Net effect on row counts:** all 1,123,066 rows are retained in the fact
table (nothing is silently dropped); the flags above (`is_zero_duration`,
`is_geo_missing`, `is_duration_capped`) let each downstream query decide
whether to include or exclude affected rows for that specific question.

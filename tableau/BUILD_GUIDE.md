# Tableau Public Dashboard — Build Guide

This is the one phase of the project I can't do for you — Tableau Public is
a GUI tool with no scripting interface, so this is a precise walkthrough
for you to execute yourself. Budget 3-4 hours the first time through.

## 0. Get the data in

1. Regenerate the extract if you haven't: `python3 src/export_tableau_extract.py`
   → produces `data/processed/tableau_extract.csv` (~1.1M rows, ~190MB).
2. Open Tableau Public Desktop → **Connect > Text File** → select that CSV.
3. Drag the single table onto the canvas. Tableau will infer types —
   double-check `date_created_ts` imported as a **Date & Time**, and
   `district_id` imported as a **String** (not a number — if Tableau
   auto-detects it as a number, right-click the field → Change Data Type →
   String, otherwise it'll try to average district IDs by accident later).
4. **Sheet 1 → bottom-left, right-click the data source → Extract** (not
   Live). An extract is what makes the published dashboard fast and
   portable — Tableau Public can't reach your local CSV once published, so
   it has to bake the data into the workbook.

## 1. KPI cards (top row)

Build 4 single-value worksheets, one measure each, then place them in a
horizontal container at the top of the dashboard:

| Card | Calculation |
|---|---|
| Median resolution time | Create a calculated field `Median Resolution Hours` = `MEDIAN([resolution_hours])`, filtered to `status_name = "Closed"` |
| Total requests (selected period) | `COUNT([incident_id])` |
| % meeting 10-day target | `AVG([met_10_day_target]) * 100` (the CSV already has this as a 0/1 flag — this was intentional, so Tableau can average it directly instead of you writing a CASE statement in every sheet) |
| Open backlog | `COUNT([incident_id])` filtered to `status_name != "Closed"` |

Format each as a **Text** worksheet: big number, small label underneath.
This is the "for a non-technical audience" requirement — a city-manager
audience wants 4 numbers at a glance before anything else.

## 2. Map — requests by location, colored by resolution time

1. New worksheet → double-click `latitude` and `longitude` (Tableau
   auto-detects these as geographic roles once named that way, or you may
   need to right-click each → Geographic Role → Latitude/Longitude).
2. Drag `resolution_hours_capped` (the winsorized column — using this
   instead of raw `resolution_hours` keeps a handful of multi-year
   outliers from blowing out the color scale) onto **Color**, aggregation
   = Average.
3. Change mark type to **Density** or keep **Circle** with size turned
   down — at 1.1M points, Density reads better than a scatter of circles.
4. Add `is_geo_missing` as a filter, excluding `True` — 57% of rows have no
   real coordinates (see `docs/data_quality_log.md` #3); leaving them in
   would put a fake cluster of points in the Gulf of Guinea.
5. This is the visual that makes the district-level regression finding
   tangible — hovering should let a viewer see exactly where the slow
   spots are, not just read it off a table.

## 3. Category drill-down (bar chart)

1. New worksheet → Rows: `service_type_name`, Columns: `Median Resolution
   Hours` (the calculated field from step 1).
2. Sort descending. Add `district_id` as a filter so this chart responds
   to a district selection elsewhere on the dashboard (set up in step 5).
3. This is the direct visual equivalent of
   `sql/analysis/01_median_p90_by_service_type.sql` — same finding, but
   clickable.

## 4. Trend line (quarterly volume + resolution time)

1. New worksheet → Columns: `year` then `quarter` (both as discrete
   dimensions, in that order, so Tableau nests them correctly on the axis).
2. Rows: `COUNT([incident_id])` as bars.
3. Dual-axis: add `Median Resolution Hours` as a line on a second axis
   (right-click the second measure's axis → Dual Axis, then Synchronize
   Axis if you want them visually comparable, or leave un-synced since
   they're different units).
4. This is the same chart already built in `notebooks/01_eda.ipynb`
   (`fig_quarterly_trend.png`) — rebuilding it in Tableau isn't redundant,
   it's what makes the same finding interactive instead of static.

## 5. Assemble the dashboard + filters

1. New Dashboard → drag in all 4 sheets above (KPI row, map, bar chart,
   trend line). Standard layout: KPI row across the top, map on the left
   taking ~half the width, bar chart and trend line stacked on the right.
2. Add filters that act on multiple sheets at once: right-click the
   `district_id` filter (from the map or bar chart) → **Apply to
   Worksheets > All Using This Data Source**. Do the same for a `year`
   filter. This is what makes it a dashboard instead of 4 separate charts —
   a viewer picks a district and every chart updates together.
3. Add a text box with the 2-3 headline findings from the README (Phase 8)
   so the dashboard is self-explanatory without you standing next to it.

## 6. Publish

1. **Server menu > Tableau Public > Save to Tableau Public**. Sign in /
   create a free account if you haven't.
2. Give the workbook a descriptive title: "San Jose 311 Response Time
   Analysis." Tableau Public workbooks are public by default — that's the
   point, it's what makes this a shareable portfolio artifact.
3. Copy the published URL and add it to the README under "Live Dashboard."

## Known limitation to state up front (don't hide it)

Only ~43% of requests have real GPS coordinates (see data quality log #3),
so the map necessarily undercounts and skews toward whichever service
types/departments happen to log location more often (mostly DOT/Parks
categories). Say this explicitly if asked in an interview — it's a real
limitation of the source data, not a bug in the pipeline.

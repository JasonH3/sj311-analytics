# Tableau Public Dashboard — Beginner Build Guide

Click-by-click instructions assuming zero prior Tableau experience. Each
step ends with a **✓ Checkpoint** telling you what you should see — if you
don't see it, stop and fix before moving on (or check Troubleshooting at
the bottom).

---

## Part 0 — The 5 ideas that make Tableau make sense

1. **Everything is drag-and-drop of "pills."** Your columns are listed in
   the **Data pane** (left). You build charts by dragging fields onto
   **shelves** (Columns, Rows, Filters — the horizontal bars at the top)
   or onto the **Marks card** buttons (Text, Color, Size). Where you drop
   a pill IS the chart definition.
2. **Blue pills = categories (dimensions), green pills = numbers
   (measures).** Blue slices data into groups; green gets aggregated
   (SUM/AVG/MEDIAN). This is why `District Id` must be a String — you
   want it to slice, not to be averaged.
3. **The Marks card controls appearance.** The dropdown on it (Automatic /
   Bar / Line / Text / Map...) sets the chart type; the Text / Color /
   Size buttons each hold one field.
4. **Double-clicking a field makes Tableau guess** where to put it, and
   it often guesses wrong. Drag deliberately instead. To undo a
   placement, drag the pill off its shelf into empty canvas space (a ✕
   appears) and release. You can never damage the underlying data.
5. **One sheet = one chart. The dashboard is just a layout grid** you
   drop finished sheets into at the end.

Also: **Cmd+Z undoes anything**, including accidental clicks. Use it
freely.

---

## Part 1 — Connect the data (one-time setup)

1. Open Tableau → left sidebar **Connect > To a File > Text file** (a CSV
   is a "text file" in Tableau's menu).
2. In the file picker press **Cmd+Shift+G**, paste
   `/Users/jasonhe/claude/sj311-analytics/data/processed/`, choose
   **tableau_extract.csv**. (If the file doesn't exist, run
   `python3 src/export_tableau_extract.py` first.)
3. On the Data Source screen, check two column types in the preview grid
   (the icon above each column name):
   - `Date Created Ts` → should show a **calendar+clock** icon. If not:
     click the icon → **Date & Time**.
   - `District Id` → must be **Abc (String)**. If it shows `#`: click the
     icon → **String**.
4. Top-right of the window: **Connection** → select **⦿ Extract**.
5. Click **Sheet 1** (bottom-left tab). Tableau asks where to save the
   extract (.hyper file) — accept the default location, wait out the
   progress bar (~1–2 min for 1.1M rows, one time only).

**✓ Checkpoint:** you're on a blank worksheet, fields listed on the left,
and everything you click from now on responds instantly.

---

## Part 2 — Four KPI sheets

These four sheets become the number cards across the top of the dashboard.
Same recipe four times; only the field and filter change.

### Sheet A: Median Resolution Hours

1. Right-click empty white space in the **Data pane** (below the field
   list) → **Create Calculated Field…**
   - Name: `Median Resolution Hours`
   - Formula: `MEDIAN([Resolution Hours])`
   - OK. (It appears in the field list with an =# icon.)
2. Drag **Status Name** from the field list and drop it on the **Filters**
   shelf. In the dialog, tick **Closed** only → OK.
3. Drag **Median Resolution Hours** from the field list and drop it on the
   **Text** button of the Marks card. (Drag-to-Text, don't double-click —
   double-clicking may scatter pills onto Rows/Columns.)
4. Make it big: click the **Text** button → click **…** next to the
   preview. In the editor you'll see `<AGG(Median Resolution Hours)>` —
   that token in angle brackets IS the number; never delete it. Select it,
   set ~28pt bold. Below it (press Enter), type a plain-text caption:
   `Median Hours to Close` at ~10pt. OK.
5. Rename the sheet: double-click the **Sheet 1** tab at the bottom →
   `KPI - Median Resolution`.

**✓ Checkpoint:** the canvas shows one big number ≈ **25.3** with your
caption under it. (That value matches the SQL median — if you see ~317,
you accidentally used AVG somewhere; if 0, check the Closed filter.)

### Sheet B: Total Requests

1. New sheet: click the **leftmost small icon with a +** just right of the
   sheet tabs at the bottom.
2. Drag **Incident Id** onto the **Text** button of the Marks card.
3. It will show as SUM (a huge nonsense number). Right-click the green
   pill on the Marks card → **Measure (Sum)** → **Count**.
4. Format big via Text → … (same as before). Caption: `Total Requests`.
5. Rename sheet: `KPI - Total Requests`.

**✓ Checkpoint:** shows **1,123,066** (all four years, no filter).

### Sheet C: % Meeting 10-Day Target

1. New sheet. Create a calculated field:
   - Name: `Pct Meeting Target`
   - Formula: `AVG([Met 10 Day Target]) * 100`
2. Drag **Pct Meeting Target** onto **Text**. Format big; caption:
   `% Closed Within 10 Days`.
3. Optional polish: Text → … → put a `%` after the token.
4. Rename sheet: `KPI - Pct Target`.

**✓ Checkpoint:** a number in the 55–60 range. (This works because
`met_10_day_target` was exported as 0/1 exactly so Tableau could AVG it.)

### Sheet D: Open Backlog

1. New sheet. Drag **Incident Id** onto **Text**; change aggregation to
   **Count** (same as Sheet B).
2. Drag **Status Name** onto **Filters** → tick everything **except**
   Closed (Open, In Progress, ReAssigned, Referred) → OK.
3. Format big; caption: `Open / Unresolved Requests`.
4. Rename sheet: `KPI - Backlog`.

**✓ Checkpoint:** ≈ **91,000** (1,123,066 total − 1,031,993 closed).

---

## Part 3 — Bar chart: median resolution by category

1. New sheet.
2. Drag **Service Type Name** onto the **Rows** shelf.
3. Drag your **Median Resolution Hours** calculated field onto the
   **Columns** shelf.
4. Drag **Status Name** onto **Filters** → tick **Closed** only.
5. Sort: hover over the "Median Resolution Hours" axis label at the
   bottom — a small sort icon appears; click until bars are longest-first.
   (Or use the sort buttons in the top toolbar.)
6. Rename sheet: `Median Hours by Category`.

**✓ Checkpoint:** horizontal bars, **Streetlight Outage near the top at
~800+ hours**, Junk pickup / Other Issues near the bottom. This is the
Tableau version of `sql/analysis/01_median_p90_by_service_type.sql`.

---

## Part 4 — Trend line: quarterly volume + median resolution

1. New sheet.
2. Drag **Year** onto **Columns**. Then drag **Quarter** onto **Columns**,
   dropping it to the RIGHT of the Year pill. If either turns green with
   SUM, right-click the pill → **Dimension** (you want them as discrete
   labels, not summed numbers).
3. Drag **Incident Id** onto **Rows**; set its aggregation to **Count**
   (right-click pill → Measure → Count).
4. Drag **Median Resolution Hours** onto **Rows**, to the right of the
   first pill. You now have two separate charts stacked.
5. Merge them: right-click the **Median Resolution Hours** pill on Rows →
   **Dual Axis**. Marks card now shows two tabs — on the CNT(Incident Id)
   tab set the dropdown to **Bar**; on the AGG(Median...) tab set it to
   **Line**.
6. Rename sheet: `Quarterly Trend`.

**✓ Checkpoint:** bars (volume) with a line (median hours) over them,
16 quarters across the x-axis, matching `docs/fig_quarterly_trend.png`
from the EDA notebook.

---

## Part 5 — Map (optional — skip if fatigued, add later)

The dashboard works without this; add it once the rest is done.

1. New sheet. Drag **Longitude** to **Columns**, **Latitude** to **Rows**.
   If Tableau shows one dot: right-click each pill → **Dimension**.
2. Drag **Is Geo Missing** onto **Filters** → tick **0** only. (57% of
   rows have no real location — data quality log #3 — and skipping this
   step is not an option: those rows would render as a fake blob in the
   ocean.)
3. Marks card dropdown → **Density**. At 480K points, a heat-style
   density map reads far better than individual circles.
4. Drag **Resolution Hours Capped** onto **Color**; right-click that
   pill → Measure → **Average**. (The capped column exists precisely so a
   few multi-year outliers don't blow out the color scale.)
5. Rename sheet: `Map`.

**✓ Checkpoint:** a recognizable San Jose street-grid heat blob — nothing
in the ocean off Africa.

---

## Part 6 — Assemble the dashboard

1. Bottom tabs → click the **middle + icon** (grid symbol) = New
   Dashboard.
2. Bottom-left **Size** panel → change Fixed Size to **Automatic**.
3. Drag sheets in from the left list, one at a time:
   - The 4 KPI sheets in a row across the top (drop zones highlight
     gray as you hover — drop side by side).
   - `Median Hours by Category` on the left half below them.
   - `Quarterly Trend` on the right half. (`Map` wherever fits if built.)
4. Make one filter control the whole dashboard: click the bar chart →
   its **funnel icon** (top-right of the selected sheet) turns the whole
   sheet into a filter — clicking a category now filters every other
   sheet. Do the same on the trend chart.
5. Add a **Text object** (from the Objects list, bottom-left) at the very
   top: dashboard title + one line per headline finding from the README.
6. Delete any stray empty "Dashboard 1" tab from earlier experiments
   (right-click tab → Delete).

**✓ Checkpoint:** clicking "Streetlight Outage" in the bar chart filters
the KPIs and trend line; clicking it again clears the filter.

---

## Part 7 — Publish

1. Menu: **Server → Tableau Public → Save to Tableau Public…** (sign in /
   create the free account when prompted).
   - If this menu item doesn't exist, you're in Tableau Desktop Free
     Edition rather than the Tableau Public app — download the Tableau
     Public app from public.tableau.com and open this same workbook file
     in it; nothing is lost.
2. Title it **"San Jose 311 Response Time Analysis"**. Remember Tableau
   Public is public by design — that's the point for a portfolio.
3. It opens in your browser when done. Copy the URL → paste it into the
   README under "Live dashboard."

---

## Troubleshooting (the greatest hits)

| Symptom | Cause | Fix |
|---|---|---|
| A mini-table with headers appeared instead of one number | Double-clicking scattered pills onto Rows/Columns | Drag those pills off the shelf into empty space (✕ appears) and release; keep the Filters one |
| The KPI number vanished, only the caption remains | The `<...>` token was deleted in the text editor | Text → … → **Insert ▾** menu → re-insert the field; tokens in `< >` are live data, plain text is just captions |
| District filter shows 1, 10, 2, 3... or tries to SUM districts | `District Id` imported as a number | Data Source tab → click the `#` above the column → String |
| Number shows ~317 instead of ~25 | AVG instead of MEDIAN (the data is right-skewed — this is finding #1 of the whole project) | Use the `MEDIAN([Resolution Hours])` calculated field |
| Map has points in the ocean / off Africa | Missing GPS was encoded as (0,0) in the source | Filter `Is Geo Missing` = 0 (Part 5 step 2) |
| A floating slider appeared | You clicked Size on the Marks card | Click anywhere else; harmless |
| Everything is slow | Still on Live connection | Data Source tab → Connection → Extract |
| Anything else weird | — | **Cmd+Z**, then re-do the step deliberately |

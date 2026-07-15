# Dashboard Restyle Guide — "Gallery Look"

Step-by-step restyle of the published dashboard to match the aesthetic of
professional Tableau gallery dashboards (Lovelytics-style corporate blue,
bordered KPI cards, header band, question-titled charts). Every step is a
formatting change — no chart gets rebuilt. Do the parts in order; each one
is independently shippable, so you can stop after any part and republish.

**Time: ~90 minutes total. Republish under the same title when done — the
URL doesn't change.**

**Final build notes — where the published dashboard deviates from this
guide, and why:** (1) Part 5's dual-axis split was evaluated and skipped —
the trend keeps its dual axis for space reasons, with both marks recolored
to the palette (muted navy bars, orange line); the trade-off is understood.
(2) Chart titles use the assertive-statement style ("Two services account
for the city's longest waits") rather than the question style — one
convention, applied consistently. (3) Bar labels are enabled on the
worksheet but suppressed by Tableau at the dashboard's card size; values
remain available via tooltips on the published interactive version.

---

## Part 0 — Pick the palette (write these down, 2 min)

Professional dashboards use ONE dark brand color, ONE accent, and grays.
Ours:

| Role | Hex | Used for |
|---|---|---|
| Navy (brand) | `#26547C` | header band, dark KPI tiles, primary bars |
| Orange (accent) | `#EB6834` | the ONE thing each chart is about (highlights, key line) |
| Light blue (muted) | `#9EC5F4` | de-emphasized bars/series |
| Page gray | `#F0EFEC` | dashboard background |
| Card white | `#FFFFFF` | every card background |
| Border gray | `#D8D6D0` | hairline card borders |
| Ink | `#333333` | titles, numbers |
| Secondary ink | `#767674` | labels, captions, axis text |

Rule that makes it look designed: **orange appears exactly once per chart**
(the highlighted bar, the key line, the number that matters). If everything
is loud, nothing is.

## Part 1 — Global reset (10 min)

1. **Fonts:** Format menu → **Workbook…** → Fonts → All → **Tableau Book**.
   Then in the same pane: Worksheet Titles → 12pt bold `#333333`.
2. **Fixed size** (if not already): Dashboard Size panel → Fixed Size →
   Generic Desktop (1366 × 768).
3. **Page background:** Format menu (with the dashboard tab active) →
   **Dashboard…** → Dashboard Shading → More colors → `#F0EFEC`.
4. **Card treatment — for every zone** (7 sheets + findings text): click
   the zone → left pane **Layout** tab →
   - Background: `#FFFFFF`
   - Border: solid, thinnest weight, `#D8D6D0`
   - Outer Padding: 8 (all sides)
   - Inner Padding: 8

**✓ Checkpoint:** white bordered cards floating on warm gray — the single
biggest step toward the reference look.

## Part 2 — Header band (15 min)

All three reference dashboards open with a full-width colored or gray band
containing the title. Ours will be navy with white text.

1. Your current title Text object: double-click it to edit. Restyle the
   text to the "Title | Subtitle" pattern from the Inventory example:
   - Line 1: `San Jose 311  |  Response Time Analysis` — 18pt bold, WHITE
     (`#FFFFFF`); make " |  Response Time Analysis" regular weight, not bold.
   - Line 2 (the how-to-read sentence): 9pt, white at ~75% (pick a light
     gray like `#D9E2EC`).
2. Click the Text object → **Layout** tab → Background: `#26547C`.
   Inner Padding: 12 left, 8 top/bottom.
3. Make the band span the full dashboard width if it doesn't already
   (drag its side edges).

**✓ Checkpoint:** a navy banner across the top, white title, like the
"Inventory Control | Overview" header.

## Part 3 — KPI cards, gallery-style (20 min)

Reference style: big number + small gray label, in a bordered card, with
ONE tile inverted (dark background, white text) to anchor the row — the
Fluctuation report does this with its dark teal tiles.

For each of the four KPI sheets (`KPI - Median Resolution`, `KPI - Total
Requests`, `KPI - Pct Target`, `KPI - Backlog`):

1. Open the sheet → Marks card → **Text** → **…** and set:
   - Number token: 22pt **semibold**, `#333333`, centered
   - Caption line: 9pt, `#767674`, centered, sentence case (`Median hours
     to close`, `Total requests`, `% closed within 10 days`,
     `Open / unresolved requests`)
2. Kill any leftover gridlines/borders inside the sheet: Format menu →
   Borders → all None; Format → Lines → all None (these sometimes draw a
   faint divider inside the card).

**The inverted anchor tile** — do this to ONE card only. The right pick is
`KPI - Backlog` (91,073 unresolved: it's the "so what" number):

3. On that sheet: Format menu → **Shading** → Worksheet: `#26547C`.
4. Text → … → number and caption both WHITE (`#FFFFFF` / light `#D9E2EC`).

**✓ Checkpoint:** four bordered KPI cards, three white + one navy, all with
identical typography. Instantly reads as the reference dashboards' KPI band.

## Part 4 — Bar chart: highlight + in-bar labels (15 min)

Reference move (Lovelytics): bars carry their value ON the bar in white,
and the important bar is a different color.

On `Median Hours by Category`:

1. **Emphasis color.** Create calculated field `Is Streetlight` =
   `[Service Type Name] = "Streetlight Outage"`. Drag it to **Color** on
   the Marks card. Edit Colors → True → `#EB6834` (orange), False →
   `#26547C` (navy). Delete/hide the True/False legend card (click its
   ✕ on the dashboard — the highlight explains itself).
2. **Labels on bars:** Marks → **Label** → Show mark labels. Click Label →
   Font: 9pt white bold; Alignment: horizontal **left**, vertical center.
   If white labels don't fit inside the shortest bars, Tableau shifts them
   outside automatically and colors them dark — that's fine; the long bars
   (the ones that matter) get the in-bar look.
3. **Kill redundant ink:** right-click the `Service Type Name` column
   header → Hide Field Labels for Rows. Right-click the bottom axis →
   uncheck Show Header (labels made it redundant). Format → Lines → Grid
   Lines: None.
4. **Question title** (Fluctuation-report style): double-click the sheet
   title → change to `Which services are slowest to close?` (12pt bold
   `#333333`).
5. Trim to earn the space: drag **Service Type Name** to Filters → Top
   tab → By field: Top **10** by `Median Resolution Hours`. Ten bars with
   labels beat twenty cramped ones. (The full list stays one click away in
   the published workbook's data.)

**✓ Checkpoint:** ten bars, nine navy + one orange (Streetlight Outage),
values printed on the bars, no axis, question as the title.

## Part 5 — Trend chart: two honest panes + end labels (15 min)

Reference move (Inventory Control): gray context line with a labeled end
point. Also: split the dual axis — two stacked panes with their own scales
read cleaner and avoid the fake-correlation look.

On `Quarterly Trend`:

1. Right-click the `AGG(Median Resolution Hours)` pill on Rows →
   **uncheck Dual Axis** (if still dual). You get two stacked panes
   sharing the quarter axis: volume on top, median below.
2. **Colors:** volume bars → muted `#9EC5F4`; median line → orange
   `#EB6834`, 2px weight (Marks → the median pane's tab → Color → Edit →
   set weight in Size).
3. **End labels** (the gallery signature): on the median pane's Marks tab →
   **Label → Show mark labels → Line Ends** (label the end of the line
   only). Font 9pt `#333333`.
4. Delete the Measure Names color legend if it's still on the dashboard —
   each pane is single-series now; the axis titles carry identity.
5. Question title: `Is the city keeping up with demand?`
6. Format → Lines → Grid Lines: None (or keep horizontal only, thinnest,
   `#E5E4DF`). Right-click the "Year / Quarter" header → Hide.

**✓ Checkpoint:** two clean stacked panes; the orange median line ends with
a printed value like the reference trend cards.

## Part 6 — Map + findings (10 min)

1. Map title → question style: `Where does demand concentrate?`
2. Map menu → Background Layers → **Washout ~50%** — the basemap recedes,
   your data advances (all three references keep geography ghost-light).
3. Findings panel: match the header band language —
   - Heading `Key findings` 11pt bold `#26547C` (navy ties it to the band)
   - Bullets 9pt `#333333`, the caveat line 8pt italic `#767674`
4. Optional (Fluctuation-report section-band look): drag a small **Text**
   object as a full-width strip above the map row, text
   `Where is the city slow — and why?`, 11pt bold `#333333`, background
   `#E5E4DF`, inner padding 8. This visually splits "the numbers" (top)
   from "the diagnosis" (bottom) the way "Where, who and why left?" does.

## Part 7 — Final pass + republish (5 min)

- Click through: every card bordered? Orange exactly once per chart? All
  captions 9pt gray? Any stray default-gray legend cards left? (Close them.)
- Test the two funnel-icon filters still work after the changes.
- Clear any active filter selections.
- **File → Save to Tableau Public As… → SAME title** → overwrites the same
  URL; the README link keeps working.

---

## The five rules that made this work (for your next dashboard)

1. Chrome first: tinted page + bordered white cards ≈ 60% of "designed."
2. One dark brand color + one accent; the accent appears once per chart.
3. Numbers big and dark; labels small and gray; nothing else bold.
4. Delete default ink (gridlines, axis titles, field labels, legends)
   until something is missed — then put only that back.
5. Titles are questions the chart answers, not descriptions of the chart.

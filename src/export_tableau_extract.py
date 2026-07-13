"""
Export a single denormalized CSV from the star schema for Tableau Public.

Why denormalize instead of pointing Tableau at the SQLite file directly:
Tableau Public doesn't support live SQLite connections, and even if it did,
re-joining 6 dimension tables on every dashboard interaction is unnecessary
overhead once the data is this size-bounded. A flat extract is also the
more universally portable artifact -- it opens the same way whether the
reviewer has Tableau Desktop, Public, or just wants to inspect it in Excel.
"""
import pathlib
import sqlite3

import pandas as pd

PROCESSED_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "processed"
DB_PATH = PROCESSED_DIR / "sj311.db"
OUT_PATH = PROCESSED_DIR / "tableau_extract.csv"

QUERY = """
SELECT
    f.incident_id,
    f.date_created_ts,
    f.latitude,
    f.longitude,
    f.is_geo_missing,
    f.resolution_hours,
    f.resolution_hours_capped,
    f.is_zero_duration,
    f.is_weekend_submission,
    ds.status_name,
    dst.service_type_name,
    dep.department_name,
    dc.channel_name,
    dd.district_id,
    dd.council_member,
    dd.population_2020,
    dt.year,
    dt.quarter,
    dt.month,
    dt.month_name,
    dt.day_name,
    CASE WHEN f.resolution_hours <= 240 THEN 1 ELSE 0 END AS met_10_day_target
FROM fact_service_requests f
JOIN dim_status ds ON f.status_id = ds.status_id
JOIN dim_service_type dst ON f.service_type_id = dst.service_type_id
JOIN dim_department dep ON f.department_id = dep.department_id
JOIN dim_channel dc ON f.channel_id = dc.channel_id
JOIN dim_date dt ON f.date_created_id = dt.date_id
LEFT JOIN dim_district dd ON f.district_id = dd.district_id
"""


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(QUERY, conn)
    conn.close()
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()

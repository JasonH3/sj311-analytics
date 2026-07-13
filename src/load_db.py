"""
Load the cleaned pandas DataFrame into the SQLite star schema defined in
sql/schema.sql.

Why build dimensions here instead of in clean.py: cleaning is about fixing
data quality; building surrogate keys is a database-loading concern. Keeping
them apart means clean.py's output is still a plain flat table you can
open in a spreadsheet, and this script's job is exactly "flat table -> star
schema," which is easy to explain as a discrete step in an interview.
"""
import pathlib
import sqlite3

import pandas as pd
from sqlalchemy import create_engine

PROCESSED_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "processed"
SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
DB_PATH = PROCESSED_DIR / "sj311.db"

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def build_dim(df: pd.DataFrame, column: str, id_column: str) -> tuple[pd.DataFrame, dict]:
    """Turns a categorical column into a small dimension table + a
    value -> surrogate key lookup for rewriting the fact table's FK."""
    values = sorted(df[column].dropna().unique())
    dim = pd.DataFrame({id_column: range(1, len(values) + 1), column: values})
    lookup = dict(zip(dim[column], dim[id_column]))
    return dim, lookup


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    all_dates = pd.date_range(df["date_created"].dt.date.min(), df["date_created"].dt.date.max(), freq="D")
    dim = pd.DataFrame({"full_date": all_dates})
    dim["date_id"] = dim["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["full_date"].dt.year
    dim["quarter"] = dim["full_date"].dt.quarter
    dim["month"] = dim["full_date"].dt.month
    dim["month_name"] = dim["month"].map(lambda m: MONTH_NAMES[m - 1])
    dim["day"] = dim["full_date"].dt.day
    dim["day_of_week"] = dim["full_date"].dt.dayofweek
    dim["day_name"] = dim["day_of_week"].map(lambda d: DAY_NAMES[d])
    dim["is_weekend"] = (dim["day_of_week"] >= 5).astype(int)
    return dim[
        ["date_id", "full_date", "year", "quarter", "month", "month_name", "day", "day_of_week", "day_name", "is_weekend"]
    ]


def build_star_schema(requests: pd.DataFrame, districts: pd.DataFrame) -> dict[str, pd.DataFrame]:
    dim_status, status_lookup = build_dim(requests, "status", "status_id")
    dim_status = dim_status.rename(columns={"status": "status_name"})

    dim_service_type, service_type_lookup = build_dim(requests, "service_type", "service_type_id")
    dim_service_type = dim_service_type.rename(columns={"service_type": "service_type_name"})

    dim_department, department_lookup = build_dim(requests, "department", "department_id")
    dim_department = dim_department.rename(columns={"department": "department_name"})

    dim_channel, channel_lookup = build_dim(requests, "channel", "channel_id")
    dim_channel = dim_channel.rename(columns={"channel": "channel_name"})

    dim_district = districts.rename(columns={"population_2020": "population_2020"})[
        ["district_id", "council_member", "population_2020"]
    ]

    dim_date = build_dim_date(requests)
    date_lookup = dict(zip(dim_date["full_date"].dt.date, dim_date["date_id"]))

    fact = pd.DataFrame(
        {
            "incident_id": requests["incident_id"],
            "date_created_id": requests["date_created"].dt.date.map(date_lookup),
            "date_created_ts": requests["date_created"],
            "date_last_updated_ts": requests["date_last_updated"],
            "status_id": requests["status"].map(status_lookup),
            "service_type_id": requests["service_type"].map(service_type_lookup),
            "department_id": requests["department"].map(department_lookup),
            "channel_id": requests["channel"].map(channel_lookup),
            "district_id": requests["district_id"],
            "latitude": requests["latitude"],
            "longitude": requests["longitude"],
            "is_geo_missing": requests["is_geo_missing"].astype(int),
            "resolution_hours": requests["resolution_hours"],
            "resolution_hours_capped": requests["resolution_hours_capped"],
            "is_zero_duration": requests["is_zero_duration"].astype(int),
            "is_duration_capped": requests["is_duration_capped"].astype(int),
            "is_weekend_submission": requests["is_weekend_submission"].astype(int),
        }
    )

    return {
        "dim_status": dim_status,
        "dim_service_type": dim_service_type,
        "dim_department": dim_department,
        "dim_channel": dim_channel,
        "dim_district": dim_district,
        "dim_date": dim_date,
        "fact_service_requests": fact,
    }


def load(tables: dict[str, pd.DataFrame]) -> None:
    DB_PATH.unlink(missing_ok=True)

    # Run the hand-written DDL first so PKs/FKs/indexes exist exactly as
    # designed, rather than letting pandas' to_sql() infer a looser schema.
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.close()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    # Load dimensions before the fact table so foreign_keys=ON doesn't
    # reject fact rows that reference a not-yet-inserted dimension key.
    load_order = [
        "dim_status", "dim_service_type", "dim_department",
        "dim_channel", "dim_district", "dim_date", "fact_service_requests",
    ]
    with engine.begin() as conn:
        for name in load_order:
            tables[name].to_sql(name, conn, if_exists="append", index=False)


def main() -> None:
    requests = pd.read_csv(
        PROCESSED_DIR / "requests_clean.csv",
        parse_dates=["date_created", "date_last_updated"],
        # Without this, read_csv infers district_id as float64 (it's a
        # numeric-looking string column with NaNs) and "10" round-trips
        # through SQLite's TEXT affinity as "10.0", breaking the join
        # against dim_district's plain "10". Force it to stay a string.
        dtype={"district_id": "string"},
    )
    districts = pd.read_csv(PROCESSED_DIR / "council_districts.csv")

    tables = build_star_schema(requests, districts)
    load(tables)

    conn = sqlite3.connect(DB_PATH)
    counts = {name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in tables}
    conn.close()
    for name, count in counts.items():
        print(f"{name}: {count:,} rows")


if __name__ == "__main__":
    main()

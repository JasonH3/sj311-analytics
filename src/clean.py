"""
Cleaning pipeline for San Jose 311 Service Request Data.

Each function here implements one row of docs/data_quality_log.md. Keeping
them separate (rather than one big transform) is deliberate: in an interview
you can point at `flag_missing_geo` and explain the (0,0)-encoding gotcha
without having to narrate the whole pipeline.
"""
import pathlib

import numpy as np
import pandas as pd

RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "processed"

YEARS = [2021, 2022, 2023, 2024]

# Data quality log #4: the CRM migration means raw Source values aren't
# comparable across years. Collapsing to two stable channels is what makes
# the app-vs-phone (self-service vs. staff-assisted) hypothesis test valid
# across the whole date range instead of just one system's naming.
CHANNEL_MAP = {
    "VBCS Web": "Self-Service Digital",
    "End-User Pages": "Self-Service Digital",
    "Web Console": "Self-Service Digital",
    "Web": "Self-Service Digital",
    "Mobile": "Self-Service Digital",
    "Live Chat": "Self-Service Digital",
    "Public API": "Self-Service Digital",
    "Oracle Integration": "Self-Service Digital",
    "Agent desktop": "Staff-Assisted",
    "CX Console": "Staff-Assisted",
    "SFDC-DOT": "Staff-Assisted",
    "Walk-ins": "Staff-Assisted",
    "Email": "Staff-Assisted",
    "Utilities": "Staff-Assisted",
}

RESOLUTION_HOURS_CAP_PERCENTILE = 99


def load_raw() -> pd.DataFrame:
    frames = []
    for year in YEARS:
        df = pd.read_csv(RAW_DIR / f"311-service-requests-{year}.csv", low_memory=False)
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    combined.columns = [c.strip().lower().replace(" ", "_") for c in combined.columns]
    return combined


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df["date_created"] = pd.to_datetime(df["date_created"], format="%m/%d/%Y %I:%M:%S %p")
    df["date_last_updated"] = pd.to_datetime(df["date_last_updated"], format="%m/%d/%Y %I:%M:%S %p")
    return df


def drop_sparse_category(df: pd.DataFrame) -> pd.DataFrame:
    """Log #1: `category` is 62.6% null; `service_type` covers the same
    concept at <1% null, so category adds no information and is dropped."""
    return df.drop(columns=["category"])


def impute_department(df: pd.DataFrame) -> pd.DataFrame:
    """Log #2: department is a near-deterministic function of service_type
    (e.g. "Pothole" -> DOT). Impute from the modal department per service
    type; anything with no non-null department anywhere stays "Unknown"
    rather than being guessed."""
    modal_dept = (
        df.dropna(subset=["department"])
        .groupby("service_type")["department"]
        .agg(lambda s: s.mode().iat[0])
    )
    df["department"] = df["department"].fillna(df["service_type"].map(modal_dept))
    df["department"] = df["department"].fillna("Unknown")
    return df


def flag_missing_geo(df: pd.DataFrame) -> pd.DataFrame:
    """Log #3: (0,0) is a real coordinate off the coast of West Africa, not
    "no location" — but that's how missing GPS is encoded here. Converting
    to NaN and flagging keeps geo/per-capita analysis from being silently
    corrupted by ~57% of rows plotting at the same false point."""
    is_missing = (df["latitude"] == 0) & (df["longitude"] == 0)
    df.loc[is_missing, ["latitude", "longitude"]] = np.nan
    df["is_geo_missing"] = is_missing
    return df


def map_channel(df: pd.DataFrame) -> pd.DataFrame:
    """Log #4: collapse the 14 raw, migration-fragmented Source values into
    two stable channels for the self-service-vs-staff-assisted comparison."""
    df["channel"] = df["source"].map(CHANNEL_MAP).fillna("Unknown")
    return df


def clean_service_type(df: pd.DataFrame) -> pd.DataFrame:
    """Log #5: "RGR?CCC" is an export artifact unique to the 2024 file.
    Recoded to an explicit Unknown/Other rather than guessed, so it's
    visible in any category-level breakdown instead of silently miscounted."""
    df["service_type"] = df["service_type"].replace("RGR?CCC", "Unknown/Other")
    df["service_type"] = df["service_type"].fillna("Unknown/Other")
    return df


def compute_resolution_hours(df: pd.DataFrame) -> pd.DataFrame:
    """Logs #6-8: resolution time is only meaningful for Closed requests
    (open ones are right-censored — their current age understates eventual
    resolution time). Zero-duration and multi-year-outlier closures are
    flagged rather than dropped, so downstream queries can choose to
    include or exclude them per question."""
    is_closed = df["status"] == "Closed"
    raw_hours = (df["date_last_updated"] - df["date_created"]).dt.total_seconds() / 3600

    df["resolution_hours"] = np.where(is_closed, raw_hours, np.nan)
    df["is_zero_duration"] = is_closed & np.isclose(raw_hours, 0)

    cap = np.nanpercentile(df.loc[is_closed, "resolution_hours"], RESOLUTION_HOURS_CAP_PERCENTILE)
    df["is_duration_capped"] = df["resolution_hours"] > cap
    df["resolution_hours_capped"] = np.where(
        df["resolution_hours"] > cap, cap, df["resolution_hours"]
    )
    return df


def add_calendar_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Weekend submissions are a plausible resolution-time driver (fewer
    staff on duty) and a natural regression feature in Phase 6."""
    df["is_weekend_submission"] = df["date_created"].dt.dayofweek >= 5
    return df


def assert_no_duplicate_incidents(df: pd.DataFrame) -> None:
    """Log #9: verified, not assumed. Fails loudly if a future data pull
    introduces duplicates a naive re-run would otherwise mask."""
    n_dupes = df["incident_id"].duplicated().sum()
    assert n_dupes == 0, f"Expected no duplicate incident_id, found {n_dupes}"


def clean() -> pd.DataFrame:
    df = load_raw()
    df = parse_dates(df)
    df = drop_sparse_category(df)
    df = impute_department(df)
    df = flag_missing_geo(df)
    df = map_channel(df)
    df = clean_service_type(df)
    df = compute_resolution_hours(df)
    df = add_calendar_flags(df)
    assert_no_duplicate_incidents(df)
    return df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df = clean()
    out_path = PROCESSED_DIR / "requests_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df):,} rows to {out_path}")
    print(df.dtypes)


if __name__ == "__main__":
    main()

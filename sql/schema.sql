-- San Jose 311 Service Requests — star schema
--
-- One fact table (fact_service_requests) at the grain of one row per
-- incident, surrounded by dimension tables for everything that's
-- repeated/categorical. This is what turns the source's single flat CSV
-- into a schema with real joins: every dimension below is a genuine
-- foreign key relationship, not just a column split off for its own sake.
--
-- Targets SQLite (see src/load_db.py) but uses only ANSI-standard DDL —
-- it runs unmodified against PostgreSQL if you swap engines later.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Dimensions
-- ---------------------------------------------------------------------

CREATE TABLE dim_status (
    status_id   INTEGER PRIMARY KEY,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_service_type (
    service_type_id   INTEGER PRIMARY KEY,
    service_type_name TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_department (
    department_id   INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE
);

-- channel_name is the *collapsed* Self-Service Digital / Staff-Assisted /
-- Unknown value (see data_quality_log.md #4), not the raw Source column —
-- the raw values aren't comparable across the 2022/2023 CRM migration.
CREATE TABLE dim_channel (
    channel_id   INTEGER PRIMARY KEY,
    channel_name TEXT NOT NULL UNIQUE
);

-- Sourced from the city's Council District GeoJSON (supplementary dataset,
-- not the 311 export). population_2020 is what makes per-capita request
-- rate queries possible.
CREATE TABLE dim_district (
    district_id     TEXT PRIMARY KEY,
    council_member  TEXT,
    population_2020 INTEGER NOT NULL
);

-- One row per calendar day spanning the dataset's date range. A date
-- dimension (rather than computing year/month/day with SQL date functions
-- in every query) is standard dimensional-modeling practice and makes
-- month-over-month / seasonal queries a plain join instead of repeated
-- strftime() calls.
CREATE TABLE dim_date (
    date_id      INTEGER PRIMARY KEY,  -- YYYYMMDD
    full_date    DATE NOT NULL UNIQUE,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    day          INTEGER NOT NULL,
    day_of_week  INTEGER NOT NULL,     -- 0=Monday .. 6=Sunday
    day_name     TEXT NOT NULL,
    is_weekend   INTEGER NOT NULL      -- 0/1
);

-- ---------------------------------------------------------------------
-- Fact
-- ---------------------------------------------------------------------

CREATE TABLE fact_service_requests (
    incident_id             INTEGER PRIMARY KEY,
    date_created_id         INTEGER NOT NULL REFERENCES dim_date(date_id),
    date_created_ts         TIMESTAMP NOT NULL,
    date_last_updated_ts    TIMESTAMP NOT NULL,
    status_id               INTEGER NOT NULL REFERENCES dim_status(status_id),
    service_type_id         INTEGER NOT NULL REFERENCES dim_service_type(service_type_id),
    department_id           INTEGER NOT NULL REFERENCES dim_department(department_id),
    channel_id              INTEGER NOT NULL REFERENCES dim_channel(channel_id),
    district_id             TEXT REFERENCES dim_district(district_id),  -- nullable: log #3, #10
    latitude                REAL,
    longitude               REAL,
    is_geo_missing          INTEGER NOT NULL,
    resolution_hours        REAL,      -- NULL unless status = Closed (log #8)
    resolution_hours_capped REAL,
    is_zero_duration        INTEGER NOT NULL,
    is_duration_capped      INTEGER NOT NULL,
    is_weekend_submission   INTEGER NOT NULL
);

CREATE INDEX idx_fact_date_created ON fact_service_requests(date_created_id);
CREATE INDEX idx_fact_status ON fact_service_requests(status_id);
CREATE INDEX idx_fact_service_type ON fact_service_requests(service_type_id);
CREATE INDEX idx_fact_department ON fact_service_requests(department_id);
CREATE INDEX idx_fact_channel ON fact_service_requests(channel_id);
CREATE INDEX idx_fact_district ON fact_service_requests(district_id);

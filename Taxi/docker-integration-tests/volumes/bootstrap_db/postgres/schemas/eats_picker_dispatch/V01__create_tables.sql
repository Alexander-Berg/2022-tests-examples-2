/* V1 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS eats_picker_dispatch;

CREATE TYPE eats_picker_dispatch.working_interval AS (
    interval_from TIMESTAMPTZ,
    interval_to TIMESTAMPTZ
);

CREATE TYPE eats_picker_dispatch.place_v1 AS (
    id BIGINT,
    revision_id BIGINT,
    slug TEXT,
    brand_id BIGINT,
    country_id BIGINT,
    region_id BIGINT,
    time_zone TEXT,
    city TEXT,
    working_intervals eats_picker_dispatch.working_interval[],
    enabled BOOL,
    updated_at TIMESTAMPTZ,
    synchronized_at TIMESTAMPTZ
);

CREATE TABLE eats_picker_dispatch.places (
    id BIGINT PRIMARY KEY,
    revision_id BIGINT NOT NULL,
    slug TEXT NOT NULL,
    brand_id BIGINT NOT NULL,
    country_id BIGINT NOT NULL,
    region_id BIGINT NOT NULL,
    time_zone TEXT NOT NULL,
    city TEXT NOT NULL,
    working_intervals eats_picker_dispatch.working_interval[] NOT NULL,
    enabled BOOL NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    synchronized_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION trigger_set_synchronized_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.synchronized_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_place_synchronized_at
BEFORE UPDATE ON eats_picker_dispatch.places
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_synchronized_at();

CREATE TABLE IF NOT EXISTS eats_picker_dispatch.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS eats_picker_dispatch.distlock_periodic_updates (
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

COMMIT;

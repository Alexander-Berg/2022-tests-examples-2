BEGIN;
CREATE SCHEMA IF NOT EXISTS eats_picker_supply;

CREATE TABLE IF NOT EXISTS eats_picker_supply.distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS eats_picker_supply.distlock_periodic_updates (
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

CREATE TYPE eats_picker_supply.picker_v1 AS (
    picker_id VARCHAR,
    name VARCHAR,
    phone_id VARCHAR,
    places_ids BIGINT[],
    available_until TIMESTAMPTZ,
    requisite_type VARCHAR,
    requisite_value VARCHAR,
    priority INTEGER,
    excluded_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    synchronized_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS eats_picker_supply.pickers(
    id BIGSERIAL PRIMARY KEY,
    picker_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    phone_id VARCHAR NOT NULL,
    places_ids BIGINT[] NOT NULL,
    available_until TIMESTAMPTZ NOT NULL,
    requisite_type VARCHAR NOT NULL,
    requisite_value VARCHAR NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    excluded_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    synchronized_at TIMESTAMPTZ NOT NULL
);
CREATE UNIQUE INDEX ix_eats_picker_supply_pickers_picker_id_unique ON eats_picker_supply.pickers (picker_id);
CREATE INDEX ix_eats_picker_supply_pickers_synchronized_at on eats_picker_supply.pickers (synchronized_at);
CREATE INDEX ix_eats_picker_supply_pickers_updated_at on eats_picker_supply.pickers (updated_at);

COMMIT;

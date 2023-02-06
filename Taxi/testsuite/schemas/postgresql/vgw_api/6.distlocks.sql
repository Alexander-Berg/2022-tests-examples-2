CREATE SCHEMA IF NOT EXISTS vgw_api;

DROP TABLE IF EXISTS vgw_api.distlocks;
CREATE TABLE vgw_api.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

DROP TABLE IF EXISTS vgw_api.distlock_periodic_updates;
CREATE TABLE vgw_api.distlock_periodic_updates (
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

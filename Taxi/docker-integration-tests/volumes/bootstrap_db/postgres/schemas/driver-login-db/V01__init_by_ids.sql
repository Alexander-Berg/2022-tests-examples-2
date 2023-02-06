CREATE SCHEMA IF NOT EXISTS driver_login;

CREATE TABLE IF NOT EXISTS driver_login.table_by_ids (
   park_id            TEXT NOT NULL,
   driver_profile_id  TEXT NOT NULL,
   last_login_at      TIMESTAMPTZ NOT NULL,
   modified_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   PRIMARY KEY (park_id, driver_profile_id)
);

CREATE INDEX IF NOT EXISTS idx_by_ids_modified_at
    ON driver_login.table_by_ids (modified_at);


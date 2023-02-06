BEGIN;

CREATE TABLE IF NOT EXISTS eats_picker_item_categories.distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS eats_picker_item_categories.distlock_periodic_updates (
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

COMMIT;

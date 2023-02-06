-- Version 2

ALTER TABLE processing.handlings
  DROP COLUMN update_metadata;

ALTER TABLE processing.handlings
  ADD COLUMN key_name TEXT NOT NULL;

CREATE TYPE processing.handle_result_v2 AS (
  scope    TEXT,
  queue    TEXT,
  item_id  TEXT,
  event_id TEXT,
  handler  TEXT,
  key      TEXT,
  enabled  BOOLEAN
);

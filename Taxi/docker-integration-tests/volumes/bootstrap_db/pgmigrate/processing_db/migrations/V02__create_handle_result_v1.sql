-- Version 1

CREATE TYPE processing.handle_result_v1 AS (
  scope    TEXT,
  queue    TEXT,
  item_id  TEXT,
  event_id TEXT,
  handler  TEXT,
  enabled  BOOLEAN
);

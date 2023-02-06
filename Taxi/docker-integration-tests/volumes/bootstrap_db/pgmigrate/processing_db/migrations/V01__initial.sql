CREATE SCHEMA processing;

-- Types

CREATE TYPE processing.new_event AS (
  scope    TEXT,
  queue    TEXT,
  item_id  TEXT,
  event_id TEXT
);

-- Distlocks

CREATE TABLE processing.dist_locks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE processing.locked_periodics (
  task_id TEXT PRIMARY KEY,
  updated TIMESTAMPTZ NOT NULL
);

-- Events

CREATE TABLE processing.events(
  scope           TEXT        NOT NULL,
  queue           TEXT        NOT NULL,
  item_id         TEXT        NOT NULL,
  event_id        TEXT        NOT NULL,

  order_key       INTEGER     NULL DEFAULT NULL,

  created         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  committed       TIMESTAMPTZ NULL DEFAULT NULL,

  payload         JSONB       NULL DEFAULT NULL,

  PRIMARY KEY (scope, queue, item_id, event_id),
  UNIQUE (scope, queue, item_id, event_id, order_key),
  CHECK ((order_key IS NULL AND committed IS NULL)
      OR (order_key IS NOT NULL AND committed IS NOT NULL))
);

CREATE INDEX all_events_for_queue
ON processing.events(scope, queue, item_id, order_key);

-- Handlings

CREATE TABLE processing.handlings(
  -- where
  scope           TEXT        NOT NULL,
  queue           TEXT        NOT NULL,
  item_id         TEXT        NOT NULL,
  event_id        TEXT        NOT NULL,

  -- what
  handler_name    TEXT        NOT NULL,

  -- when
  handled         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- outcomes
  handler_enabled BOOLEAN     NOT NULL,
  update_metadata JSONB       NULL DEFAULT NULL,

  PRIMARY KEY(scope, queue, item_id, event_id, handler_name),

  FOREIGN KEY(scope, queue, item_id, event_id)
    REFERENCES processing.events(scope, queue, item_id, event_id)
    ON DELETE CASCADE ON UPDATE RESTRICT
);

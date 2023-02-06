-- Version 4

DROP TABLE processing.handlings;

CREATE TABLE processing.processing_state(
  scope            TEXT        NOT NULL,
  queue            TEXT        NOT NULL,
  item_id          TEXT        NOT NULL,
  event_id         TEXT        NOT NULL,

  pipeline         TEXT        NULL,
  condition_key    TEXT        NULL,
  condition_reason TEXT        NULL,

  shared_state     JSONB       NULL,
  stage            TEXT        NULL,

  finshed_handlers TEXT[]      NULL,
  handlers_result  JSONB       NULL,

  PRIMARY KEY(scope, queue, item_id, event_id),

  FOREIGN KEY(scope, queue, item_id, event_id)
    REFERENCES processing.events(scope, queue, item_id, event_id)
    ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE TYPE processing.new_event_v3 AS (
  scope             TEXT,
  queue             TEXT,
  item_id           TEXT,
  event_id          TEXT,
  idempotency_token TEXT,
  need_handle       BOOLEAN
);

CREATE TYPE processing.item_locator_v1 AS (
  scope    TEXT,
  queue    TEXT,
  item_id  TEXT
);

CREATE TYPE processing.processing_state_upsert_v1 AS (
  event_id         TEXT,
  pipeline         TEXT,
  condition_key    TEXT,
  condition_reason TEXT,
  shared_state     JSONB,
  stage            TEXT,
  finshed_handlers TEXT[],
  handlers_result  JSONB
);

ALTER TABLE processing.events
  ADD COLUMN need_handle BOOLEAN NOT NULL;

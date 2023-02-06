CREATE SCHEMA processing_noncritical;

CREATE TABLE processing_noncritical.processing_state(
  scope            TEXT        NOT NULL,
  queue            TEXT        NOT NULL,
  item_id          TEXT        NOT NULL,

  event_id         TEXT        NOT NULL,
  pipeline         TEXT        NULL,
  condition_key    TEXT        NULL,
  condition_reason TEXT        NULL,

  shared_state     TEXT        NULL,
  stage            TEXT        NULL,

  finshed_handlers TEXT[]      NULL,
  handlers_result  TEXT        NULL,

  PRIMARY KEY(scope, queue, item_id)
);

CREATE TYPE processing_noncritical.item_locator_v1 AS (
  scope    TEXT,
  queue    TEXT,
  item_id  TEXT
);


CREATE TYPE processing_noncritical.processing_state_upsert_v2 AS (
  event_id         TEXT,
  pipeline         TEXT,
  condition_key    TEXT,
  condition_reason TEXT,
  shared_state     TEXT,
  stage            TEXT,
  finshed_handlers TEXT[],
  handlers_result  TEXT
);

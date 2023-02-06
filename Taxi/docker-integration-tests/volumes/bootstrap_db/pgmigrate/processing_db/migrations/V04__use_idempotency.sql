-- Version 3

ALTER TABLE processing.events DROP COLUMN committed;

ALTER TABLE processing.events
  ADD COLUMN idempotency_token TEXT NOT NULL;

ALTER TABLE processing.events
  ADD CONSTRAINT unique_idempotency_token
  UNIQUE (scope, queue, item_id, idempotency_token);

CREATE TYPE processing.new_event_v2 AS (
  scope             TEXT,
  queue             TEXT,
  item_id           TEXT,
  event_id          TEXT,
  idempotency_token TEXT
);

ALTER TABLE processing.events
  ADD CONSTRAINT unique_order_key_for_item
  UNIQUE (scope, queue, item_id, order_key);

ALTER TABLE processing.events ALTER COLUMN order_key SET NOT NULL;

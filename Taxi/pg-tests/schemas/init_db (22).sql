CREATE SCHEMA processing;

CREATE TABLE processing.events(
  scope           TEXT        NOT NULL,
  queue           TEXT        NOT NULL,
  item_id         TEXT        NOT NULL,
  event_id        TEXT        NOT NULL,

  PRIMARY KEY (scope, queue, item_id, event_id)
);

ALTER TABLE processing.events
  ADD COLUMN updated TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE processing.events
  ADD COLUMN is_archivable BOOLEAN NOT NULL DEFAULT FALSE;

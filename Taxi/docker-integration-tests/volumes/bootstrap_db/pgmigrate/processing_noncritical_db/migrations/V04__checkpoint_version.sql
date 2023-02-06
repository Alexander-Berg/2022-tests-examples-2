ALTER TABLE processing_noncritical.processing_state
  ADD COLUMN handle_by_version TEXT NULL DEFAULT NULL;

CREATE TYPE processing_noncritical.processing_state_upsert_v4 AS (
  event_id          TEXT,
  handle_by_version TEXT,
  pipeline          TEXT,
  condition_key     TEXT,
  condition_reason  TEXT,
  shared_state      BYTEA,
  stage             TEXT,
  finshed_handlers  TEXT[],
  handlers_result   BYTEA
);

ALTER TABLE processing_noncritical.processing_tasks_state_v1
  ADD COLUMN handle_by_version TEXT NULL DEFAULT NULL;

CREATE TYPE processing_noncritical.processing_tasks_state_upsert_v2 AS (
  handle_by_version      TEXT,
  shared_state_bson      BYTEA,
  stage                  TEXT,
  finished_handlers      TEXT[],
  handlers_result_bson   BYTEA
);



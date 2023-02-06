ALTER TABLE processing_noncritical.processing_state
  ADD COLUMN shared_state_bson bytea;

ALTER TABLE processing_noncritical.processing_state
  ADD COLUMN handlers_result_bson bytea;

CREATE TYPE processing_noncritical.processing_state_upsert_v3 AS (
  event_id         TEXT,
  pipeline         TEXT,
  condition_key    TEXT,
  condition_reason TEXT,
  shared_state     BYTEA,
  stage            TEXT,
  finshed_handlers TEXT[],
  handlers_result  BYTEA
);

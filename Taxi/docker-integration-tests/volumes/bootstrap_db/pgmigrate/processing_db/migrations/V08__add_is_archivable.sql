-- add column

ALTER TABLE processing.events
  ADD COLUMN is_archivable BOOLEAN NOT NULL DEFAULT FALSE;

-- update function

CREATE OR REPLACE FUNCTION processing.create_event(
  IN new_event processing.new_event_v3,
  IN event_kind processing.event_kind_v1,
  IN event_payload JSONB) RETURNS TEXT AS $$
DECLARE
  writable BOOLEAN;
  became_archivable BOOLEAN;
BEGIN
  writable := processing.is_writable_item(new_event.scope,
                                          new_event.queue,
                                          new_event.item_id);

  -- check preconditions
  IF event_kind = 'user' AND NOT writable THEN
    RETURN 'not_writable';
  ELSIF event_kind IN ('create', 'reopen') AND writable THEN
    RETURN 'already_writable';
  ELSIF event_kind = 'finish' AND NOT writable THEN
    RETURN 'already_not_writable';
  END IF;

  -- perform event insertion
  WITH max_order_key AS (
    SELECT COALESCE(MAX(e.order_key), -1) AS value
    FROM processing.events AS e
    WHERE e.scope = new_event.scope
      AND e.queue = new_event.queue
      AND e.item_id = new_event.item_id
  )
  INSERT INTO processing.events(scope, queue, item_id, event_id, order_key,
                                idempotency_token, payload, need_handle, event_kind)
  SELECT new_event.scope, new_event.queue, new_event.item_id,
         new_event.event_id, mok.value + 1, new_event.idempotency_token,
         event_payload, new_event.need_handle, event_kind
  FROM max_order_key AS mok;

  -- maybe update is_archivable flag
  IF event_kind in ('finish', 'reopen') THEN
    became_archivable := event_kind = 'finish';
    UPDATE processing.events
    SET is_archivable = became_archivable
    WHERE scope = new_event.scope AND
          queue = new_event.queue AND
          item_id = new_event.item_id;
  END IF;

  RETURN 'success';
END;
$$ LANGUAGE plpgsql;

-- init values (if any)

DO $$
DECLARE
  rec RECORD;
  writeable BOOLEAN;
BEGIN
  FOR rec IN
    SELECT DISTINCT scope, queue, item_id FROM processing.events
  LOOP
    writeable := processing.is_writable_item(rec.scope, rec.queue, rec.item_id);
    UPDATE processing.events SET is_archivable = NOT writeable
    WHERE scope = rec.scope AND
          queue = rec.queue AND
          item_id = rec.item_id;
  END LOOP;
END$$;


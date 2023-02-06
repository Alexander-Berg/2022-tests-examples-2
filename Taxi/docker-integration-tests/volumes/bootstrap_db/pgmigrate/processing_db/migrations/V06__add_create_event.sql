-- add updated column

ALTER TABLE processing.events
  ADD COLUMN updated TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX processing_events_updated_idx  ON processing.events(updated);

-- add event kind column

CREATE TYPE processing.event_kind_v1 AS ENUM ('create', 'user', 'finish', 'reopen');

ALTER TABLE processing.events
  ADD COLUMN event_kind processing.event_kind_v1 NOT NULL DEFAULT 'user';

-- queue writability checker

CREATE FUNCTION processing.is_writable_item(IN scope_ TEXT,
                                            IN queue_ TEXT,
                                            IN item_id_ TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  item_event RECORD;
  result BOOLEAN;
BEGIN
  result := FALSE;

  FOR item_event IN
    SELECT e.event_kind FROM processing.events AS e
    WHERE e.scope = scope_ AND e.queue = queue_ AND e.item_id = item_id_
    ORDER BY e.order_key ASC
  LOOP
    IF item_event.event_kind IN ('create', 'reopen') THEN
      result := TRUE;
    ELSIF item_event.event_kind = 'finish' THEN
      result := FALSE;
    END IF;
  END LOOP;

  RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION processing.create_event(
  IN new_event processing.new_event_v3,
  IN event_kind processing.event_kind_v1,
  IN event_payload JSONB) RETURNS TEXT AS $$
DECLARE
  writable BOOLEAN;
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

  RETURN 'success';
END;
$$ LANGUAGE plpgsql;

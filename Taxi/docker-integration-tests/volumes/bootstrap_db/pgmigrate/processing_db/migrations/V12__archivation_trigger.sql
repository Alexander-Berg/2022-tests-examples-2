CREATE FUNCTION processing.is_can_be_archived(IN scope_ TEXT,
                                              IN queue_ TEXT,
                                              IN item_id_ TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  item_event RECORD;
  result BOOLEAN;
BEGIN
  result := TRUE;

  FOR item_event IN
    SELECT e.event_kind, e.need_handle FROM processing.events AS e
    WHERE e.scope = scope_ AND e.queue = queue_ AND e.item_id = item_id_
    ORDER BY e.order_key ASC
  LOOP
    IF item_event.need_handle THEN
      RETURN FALSE;
    END IF;

    IF item_event.event_kind IN ('create', 'reopen') THEN
      result := FALSE;
    ELSIF item_event.event_kind = 'finish' THEN
      result := TRUE;
    END IF;
  END LOOP;

  RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION processing.update_is_archivable()
RETURNS TRIGGER AS $body$
BEGIN
  IF processing.is_can_be_archived(NEW.scope, NEW.queue, NEW.item_id)
  THEN
    UPDATE processing.events
    SET is_archivable = TRUE
    WHERE scope = NEW.scope AND queue = NEW.queue AND item_id = NEW.item_id;
  END IF;
  RETURN NEW;
END;
$body$ LANGUAGE plpgsql;

CREATE TRIGGER update_archivable_after_handling
  AFTER UPDATE OF need_handle ON processing.events FOR EACH ROW
  EXECUTE PROCEDURE processing.update_is_archivable();

--

CREATE OR REPLACE FUNCTION processing.create_event(
  IN new_event processing.new_event_v3,
  IN event_kind processing.event_kind_v1,
  IN event_payload JSONB) RETURNS TEXT AS $$
DECLARE
  writable BOOLEAN;
  became_archivable BOOLEAN;
BEGIN
  -- check idempotency key uniqness
  IF EXISTS(SELECT FROM processing.events
            WHERE scope = new_event.scope
              AND queue = new_event.queue
              AND item_id = new_event.item_id
              AND idempotency_token = new_event.idempotency_token)
  THEN
    RETURN 'already_exists';
  END IF;

  -- evaluate writabillity
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
  IF event_kind = 'reopen' OR
     (event_kind = 'finish' AND NOT new_event.need_handle)
  THEN
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

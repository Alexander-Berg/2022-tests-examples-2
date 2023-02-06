-- Archivation service depend on an assumption that all event of single item
-- will have same value of is_archivable at any moment of time.
-- Archivation may work incorrectly if we fail to hold this assumption.
CREATE FUNCTION processing.update_is_archivable(
    IN scope_ TEXT,
    IN queue_ TEXT,
    IN item_id_ TEXT) RETURNS VOID AS $$
DECLARE
    all_events_archivable BOOLEAN;
BEGIN
    all_events_archivable := NOT EXISTS (
        SELECT FROM processing.events
        WHERE scope = scope_
          AND queue = queue_
          AND item_id = item_id_
          AND need_handle);

    UPDATE processing.events
    SET is_archivable = all_events_archivable
    WHERE scope = scope_
      AND queue = queue_
      AND item_id = item_id_;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION processing.create_event_v3(
    IN new_event processing.new_event_v4,
    IN event_payload JSONB,
    IN check_fellow_events BOOLEAN)
RETURNS TEXT AS $$
BEGIN
    -- check uniqness of idempotency token
    IF EXISTS(SELECT FROM processing.events
              WHERE scope = new_event.scope
                AND queue = new_event.queue
                AND item_id = new_event.item_id
                AND idempotency_token = new_event.idempotency_token)
    THEN
        RETURN 'already_exists';
    END IF;

    -- maybe archived or mis-sharding
    IF check_fellow_events THEN
        IF NOT EXISTS(SELECT FROM processing.events
                      WHERE scope = new_event.scope
                        AND queue = new_event.queue
                        AND item_id = new_event.item_id
                      LIMIT 1)
        THEN
            RETURN 'no_fellow_events';
        END IF;
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
                                  idempotency_token, payload, need_handle, due)
    SELECT new_event.scope, new_event.queue, new_event.item_id,
           new_event.event_id, mok.value + 1, new_event.idempotency_token,
           event_payload, new_event.need_handle, new_event.due
    FROM max_order_key AS mok;

    -- update is_archivable flags
    PERFORM processing.update_is_archivable(new_event.scope,
                                            new_event.queue,
                                            new_event.item_id);
    RETURN 'success';
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION processing.mark_handled_v2(
    IN item_locator processing.item_locator_v1,
    IN event_ids TEXT[])
RETURNS VOID AS $$
BEGIN
    -- update need_handle flags
    UPDATE processing.events SET need_handle = FALSE, updated = NOW()
    WHERE scope = item_locator.scope
      AND queue = item_locator.queue
      AND item_id = item_locator.item_id
      AND event_id IN (SELECT(UNNEST(event_ids)));

    -- update is_archivable flags
    PERFORM processing.update_is_archivable(item_locator.scope,
                                            item_locator.queue,
                                            item_locator.item_id);
END;
$$ LANGUAGE plpgsql;

CREATE TYPE processing.event_from_yt_v2 AS (
    scope             TEXT,
    queue             TEXT,
    item_id           TEXT,
    event_id          TEXT,
    order_key         INTEGER,
    created           TIMESTAMPTZ,
    payload           JSONB,
    idempotency_token TEXT,
    need_handle       BOOLEAN,
    is_archivable     BOOLEAN,
    due               TIMESTAMPTZ
);

-- Assuming that restore process will be triggered when no "create"
-- event in the table. Which means that there may be (or not) some
-- other events for a given (scope, queue, item_id). These events
-- was created when no "archived" events persists which means that
-- event_key for them started from 0. This situation will cause
-- conflict with restored events (since they are also counted from 0).
-- That why this function will shift order_key of existing events
-- to give space for events which will arrive from YT.
CREATE FUNCTION processing.restore_events_v2(
    IN events processing.event_from_yt_v2[]) RETURNS VOID AS $$
DECLARE
    item RECORD;
BEGIN
    -- advance order key of existing events
    SET CONSTRAINTS processing.unique_order_key_for_item DEFERRED;
    WITH order_key_fix AS (
        SELECT scope, queue, item_id, MAX(order_key) max_order_key
        FROM UNNEST(events)
        GROUP BY scope, queue, item_id) 
    UPDATE processing.events AS dst
    SET order_key = order_key + order_key_fix.max_order_key + 1,
        updated = NOW()
    FROM order_key_fix
    WHERE dst.scope = order_key_fix.scope
      AND dst.queue = order_key_fix.queue
      AND dst.item_id = order_key_fix.item_id;

    -- insert events from YT
    SET CONSTRAINTS processing.unique_order_key_for_item IMMEDIATE;
    INSERT INTO processing.events(scope,
                                  queue,
                                  item_id,
                                  event_id,
                                  order_key,
                                  created,
                                  payload,
                                  idempotency_token,
                                  need_handle,
                                  updated,
                                  is_archivable,
                                  due)
    SELECT scope,
           queue,
           item_id,
           event_id,
           order_key,
           created, 
           payload,
           idempotency_token,
           need_handle,
           NOW(),
           is_archivable,
           due
    FROM UNNEST(events)
    ON CONFLICT ON CONSTRAINT events_pkey DO NOTHING;

    -- update is_archivable flags
    FOR item IN (SELECT DISTINCT scope, queue, item_id FROM UNNEST(events))
    LOOP
      PERFORM processing.update_is_archivable(item.scope,
                                              item.queue,
                                              item.item_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE TYPE processing.queue_event_v2 AS(
    event_id    TEXT,
    created     TIMESTAMPTZ,
    need_handle BOOLEAN,
    payload     JSONB
);

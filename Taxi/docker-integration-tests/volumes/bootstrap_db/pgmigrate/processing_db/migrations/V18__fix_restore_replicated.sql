-- Assuming that restore process will be triggered when no "create"
-- event in the table. Which means that there may be (or not) some
-- other events for a given (scope, queue, item_id). These events
-- was created when no "archived" events persists which means that
-- event_key for them started from 0. This situation will cause
-- conflict with restored events (since they are also counted from 0).
-- That why this function will shift order_key of existing events
-- to give space for events which will arrive from YT.
--
-- This method relies on atomicy of archivation's DELETE operation
-- for a given (scope, queue, item_id). Partial delete may result in
-- inconsistent state of events sequence.
CREATE FUNCTION processing.restore_events_v3(
    IN source_events processing.event_from_yt_v2[]) RETURNS VOID AS $$
DECLARE
    item RECORD;
BEGIN
    -- advance order key of existing events
    SET CONSTRAINTS processing.unique_order_key_for_item DEFERRED;
    WITH order_key_fix AS (
        SELECT scope, queue, item_id, MAX(order_key) max_order_key
        FROM UNNEST(source_events)
        GROUP BY scope, queue, item_id) 
    UPDATE processing.events AS dst
    SET order_key = order_key + order_key_fix.max_order_key + 1,
        updated = NOW()
    FROM order_key_fix
    WHERE dst.scope = order_key_fix.scope
      AND dst.queue = order_key_fix.queue
      AND dst.item_id = order_key_fix.item_id;
    SET CONSTRAINTS processing.unique_order_key_for_item IMMEDIATE;

    -- insert events from YT
    WITH existing_events AS (
        SELECT scope, queue, item_id, idempotency_token
        FROM processing.events
        WHERE (scope, queue, item_id) IN (
            SELECT DISTINCT scope, queue, item_id
            FROM UNNEST(source_events)))
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
    SELECT se.scope,
           se.queue,
           se.item_id,
           se.event_id,
           se.order_key,
           se.created, 
           se.payload,
           se.idempotency_token,
           se.need_handle,
           NOW(),
           se.is_archivable,
           se.due
    FROM UNNEST(source_events) AS se
    WHERE (se.scope, se.queue, se.item_id, se.idempotency_token) NOT IN (
        SELECT ee.scope, ee.queue, ee.item_id, ee.idempotency_token
        FROM existing_events AS ee);

    -- update is_archivable flags
    FOR item IN (SELECT DISTINCT scope, queue, item_id
                 FROM UNNEST(source_events))
    LOOP
      PERFORM processing.update_is_archivable(item.scope,
                                              item.queue,
                                              item.item_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- make constraint 'unique_order_key_for_item' deferrable

ALTER TABLE processing.events
  DROP CONSTRAINT unique_order_key_for_item;

ALTER TABLE processing.events
  ADD CONSTRAINT unique_order_key_for_item
  UNIQUE (scope, queue, item_id, order_key)
  DEFERRABLE;

-- define type for YT representation of event

CREATE TYPE processing.event_from_yt_v1 AS (
    scope             TEXT,
    queue             TEXT,
    item_id           TEXT,
    event_id          TEXT,
    order_key         INTEGER,
    created           TIMESTAMPTZ,
    payload           JSONB,
    idempotency_token TEXT,
    need_handle       BOOLEAN,
    event_kind        processing.event_kind_v1,
    is_archivable     BOOLEAN,
    due               TIMESTAMPTZ
);

-- define events restoration function

-- Assuming that restore process will be triggered by "reopen" event
-- which means that there is at least "reopen" event in table. Since
-- table was empty at the moment when "reopen" (and followed) events
-- were added they have order_key count started from 0. This function
-- will shift order_key of existing events to give space for events
-- arraived from YT.
CREATE FUNCTION processing.restore_events_v1(
    IN events processing.event_from_yt_v1[]) RETURNS VOID AS $$
BEGIN
  -- advance order key of existing events.
  -- don't advance 'create' event, it will always stay at order_key = 0
  -- which will cause constraint violation in case of races
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
    AND dst.item_id = order_key_fix.item_id
    AND dst.event_kind != 'create';

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
                                event_kind,
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
         event_kind,
         is_archivable,
         due
  FROM UNNEST(events)
  ON CONFLICT ON CONSTRAINT events_pkey DO NOTHING;
END;
$$ LANGUAGE plpgsql;

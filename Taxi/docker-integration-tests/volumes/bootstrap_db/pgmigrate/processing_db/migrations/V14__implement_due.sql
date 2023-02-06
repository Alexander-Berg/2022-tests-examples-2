ALTER TABLE processing.events
ADD COLUMN due TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE TYPE processing.new_event_v4 AS (
    scope             TEXT,
    queue             TEXT,
    item_id           TEXT,
    event_id          TEXT,
    idempotency_token TEXT,
    need_handle       BOOLEAN,
    due               TIMESTAMPTZ
);

CREATE FUNCTION processing.create_event_v2(
    IN new_event processing.new_event_v4,
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
                                  idempotency_token, payload, need_handle, event_kind, due)
    SELECT new_event.scope, new_event.queue, new_event.item_id,
           new_event.event_id, mok.value + 1, new_event.idempotency_token,
           event_payload, new_event.need_handle, event_kind, new_event.due
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

CREATE TYPE processing.queue_event_v1 AS(
    event_id TEXT,
    created TIMESTAMPTZ,
    need_handle BOOLEAN,
    event_kind processing.event_kind_v1,
    payload JSONB
);

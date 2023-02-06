CREATE TYPE processing.queue_event_v3 AS(
    event_id    TEXT,
    created     TIMESTAMPTZ,
    updated     TIMESTAMPTZ,
    need_handle BOOLEAN,
    order_key   INTEGER,
    payload     JSONB
);

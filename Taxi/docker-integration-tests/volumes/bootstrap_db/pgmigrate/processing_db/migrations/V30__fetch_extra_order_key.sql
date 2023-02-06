-- add 'extra_order_key' field to processing.queue_event_v7
CREATE TYPE processing.queue_event_v8 AS(
    event_id           TEXT,
    created            TIMESTAMPTZ,
    updated            TIMESTAMPTZ,
    due                TIMESTAMPTZ,
    need_handle        BOOLEAN,
    order_key          INTEGER,
    is_malformed       BOOLEAN,
    is_duplicate       BOOLEAN,
    handling_order_key INTEGER,
    extra_order_key    INTEGER,
    payload            JSONB
);

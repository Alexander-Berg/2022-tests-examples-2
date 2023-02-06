-- like processing.queue_event_v6 but with 'due' field
CREATE TYPE processing.queue_event_v7 AS(
    event_id           TEXT,
    created            TIMESTAMPTZ,
    updated            TIMESTAMPTZ,
    due                TIMESTAMPTZ,
    need_handle        BOOLEAN,
    order_key          INTEGER,
    is_malformed       BOOLEAN,
    is_duplicate       BOOLEAN,
    handling_order_key INTEGER,
    payload            JSONB
);

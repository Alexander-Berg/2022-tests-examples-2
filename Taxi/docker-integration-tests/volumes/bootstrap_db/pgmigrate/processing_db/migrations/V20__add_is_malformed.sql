CREATE TYPE processing.queue_event_v4 AS(
    event_id     TEXT,
    created      TIMESTAMPTZ,
    updated      TIMESTAMPTZ,
    need_handle  BOOLEAN,
    order_key    INTEGER,
    is_malformed BOOLEAN,
    payload      JSONB
);

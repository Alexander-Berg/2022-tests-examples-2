CREATE TYPE processing.queue_event_v10 AS (
    event_id TEXT,
    order_key INTEGER,
    created TIMESTAMPTZ,
    payload JSONB,
    idempotency_token TEXT,
    need_handle BOOLEAN,
    updated TIMESTAMPTZ,
    due TIMESTAMPTZ,
    is_malformed BOOLEAN,
    extra_order_key INTEGER,
    handling_order_key INTEGER,
    is_duplicate BOOLEAN,
    handling_counters  jsonb
);

CREATE TYPE processing.event_from_yt_v6 AS (
    scope              TEXT,
    queue              TEXT,
    item_id            TEXT,
    event_id           TEXT,
    order_key          INTEGER,
    created            TIMESTAMPTZ,
    payload            JSONB,
    idempotency_token  TEXT,
    need_handle        BOOLEAN,
    updated            TIMESTAMPTZ,
    is_archivable      BOOLEAN,
    due                TIMESTAMPTZ,
    extra_order_key    INTEGER,
    handling_order_key INTEGER,
    is_duplicate       BOOLEAN
);

ALTER TABLE processing.events
ADD COLUMN is_duplicate BOOLEAN DEFAULT FALSE;

-- like processing.queue_event_v5 but with 'is_duplicate' field
CREATE TYPE processing.queue_event_v6 AS(
    event_id           TEXT,
    created            TIMESTAMPTZ,
    updated            TIMESTAMPTZ,
    need_handle        BOOLEAN,
    order_key          INTEGER,
    is_malformed       BOOLEAN,
    is_duplicate       BOOLEAN,
    handling_order_key INTEGER,
    payload            JSONB
);

-- like processing.event_from_yt_v4 but with 'is_duplicate' field
CREATE TYPE processing.event_from_yt_v5 AS (
    scope              TEXT,
    queue              TEXT,
    item_id            TEXT,
    event_id           TEXT,
    order_key          INTEGER,
    created            TIMESTAMPTZ,
    payload            JSONB,
    idempotency_token  TEXT,
    need_handle        BOOLEAN,
    is_archivable      BOOLEAN,
    due                TIMESTAMPTZ,
    handling_order_key INTEGER,
    extra_order_key    INTEGER,
    is_duplicate       BOOLEAN
);

ALTER TABLE processing.events
ADD COLUMN handling_order_key INTEGER NULL DEFAULT NULL;

CREATE TYPE processing.queue_event_v5 AS(
    event_id           TEXT,
    created            TIMESTAMPTZ,
    updated            TIMESTAMPTZ,
    need_handle        BOOLEAN,
    order_key          INTEGER,
    is_malformed       BOOLEAN,
    handling_order_key INTEGER,
    payload            JSONB
);

CREATE TYPE processing.event_from_yt_v4 AS (
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
    extra_order_key    INTEGER
);

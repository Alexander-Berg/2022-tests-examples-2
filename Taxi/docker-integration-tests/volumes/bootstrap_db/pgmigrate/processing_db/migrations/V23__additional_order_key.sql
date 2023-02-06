ALTER TABLE processing.events
ADD COLUMN extra_order_key INTEGER DEFAULT NULL;

CREATE TYPE processing.new_event_v5 AS (
    scope             TEXT,
    queue             TEXT,
    item_id           TEXT,
    event_id          TEXT,
    idempotency_token TEXT,
    need_handle       BOOLEAN,
    due               TIMESTAMPTZ,
    extra_order_key   INTEGER
);

CREATE TYPE processing.event_from_yt_v3 AS (
    scope             TEXT,
    queue             TEXT,
    item_id           TEXT,
    event_id          TEXT,
    order_key         INTEGER,
    created           TIMESTAMPTZ,
    payload           JSONB,
    idempotency_token TEXT,
    need_handle       BOOLEAN,
    is_archivable     BOOLEAN,
    due               TIMESTAMPTZ,
    extra_order_key   INTEGER
);

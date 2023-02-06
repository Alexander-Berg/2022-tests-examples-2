ALTER TABLE processing.events
ADD COLUMN reschedule_due TIMESTAMPTZ NULL DEFAULT NULL;

ALTER TABLE processing.events
ADD COLUMN handling_counters JSONB NULL DEFAULT NULL;

-- like processing.queue_event_v8 but with 'handling_counters' field
CREATE TYPE processing.queue_event_v9 AS(
    event_id           text,
    created            timestamp with time zone,
    updated            timestamp with time zone,
    due                timestamp with time zone,
    need_handle        boolean,
    order_key          integer,
    is_malformed       boolean,
    is_duplicate       boolean,
    handling_order_key integer,
    extra_order_key    integer,
    payload            jsonb,
    handling_counters  jsonb
);

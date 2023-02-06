CREATE TABLE events.grocery_event_bus_events_production_grocery_performer_shift_update
(
    depot_id String,
    timestamp Nullable(DateTime),
    performer_id Nullable(String),
    shift_id Nullable(String),
    status Nullable(String),
    shift_type Nullable(String)
)
ENGINE = MergeTree
ORDER BY (depot_id, performer_id)
SETTINGS allow_nullable_key = 1, index_granularity = 8192

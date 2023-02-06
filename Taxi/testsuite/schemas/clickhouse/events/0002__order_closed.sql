CREATE TABLE events.grocery_event_bus_events_production_grocery_order_closed
(
    order_id String,
    depot_id String,
    timestamp Nullable(DateTime),
    is_canceled Nullable(UInt8),
    cancel_reason_type Nullable(String),
    cancel_reason_message Nullable(String)
)
ENGINE = MergeTree
ORDER BY (depot_id, order_id)
SETTINGS allow_nullable_key = 1, index_granularity = 8192

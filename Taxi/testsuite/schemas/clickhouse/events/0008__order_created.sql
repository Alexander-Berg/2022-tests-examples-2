CREATE TABLE events.grocery_event_bus_events_production_grocery_order_created
(
    order_id String,
    depot_id String,
    timestamp Nullable(DateTime),
    max_eta Nullable(Int32),
    delivery_type Nullable(String)
)
ENGINE = MergeTree
ORDER BY (depot_id, order_id)
SETTINGS allow_nullable_key = 1, index_granularity = 8192

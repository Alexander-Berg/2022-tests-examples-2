CREATE TABLE events.grocery_event_bus_events_production_grocery_performer_pickup_order
(
    order_id String,
    depot_id String,
    timestamp Nullable(DateTime),
    performer_id Nullable(String)
)
ENGINE = MergeTree
ORDER BY (depot_id, performer_id, order_id)
SETTINGS allow_nullable_key = 1, index_granularity = 8192

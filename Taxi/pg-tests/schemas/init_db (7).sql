CREATE SCHEMA IF NOT EXISTS eats_orders_tracking;

CREATE TABLE IF NOT EXISTS eats_orders_tracking.waybills
(
    waybill_ref TEXT PRIMARY KEY,
    points JSONB NOT NULL,
    performer_info JSONB NOT NULL,
    order_nrs TEXT[] NOT NULL,
    chained_previous_waybill_ref TEXT,
    waybill_revision INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eats_orders_tracking.shared_tracking_links
(
    shared_id TEXT PRIMARY KEY,
    order_nr TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE eats_orders_tracking.idempotency_keys (
    idempotency_key TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

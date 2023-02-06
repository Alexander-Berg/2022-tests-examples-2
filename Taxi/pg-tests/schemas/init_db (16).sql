CREATE SCHEMA orders_tracking;

CREATE TYPE orders_tracking.informer_type AS ENUM (
    'bad_weather',
    'long_courier_search',
    'long_courier_search_promocode',
    'long_delivery',
    'long_delivery_promocode',
    'late_order_promocode',
    'compensation',
    'cancel'
);

CREATE TYPE orders_tracking.compensation_type AS ENUM (
    'promocode',
    'voucher',
    'full_voucher',
    'super_voucher',
    'super_plus_voucher',
    'refund',
    'full_refund',
    'tips_refund',
    'delivery_refund'
);

CREATE TABLE orders_tracking.informers (
    order_id TEXT NOT NULL,
    informer_type orders_tracking.informer_type NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    compensation_type orders_tracking.compensation_type NULL,
    situation_code TEXT NULL,
    cancel_reason TEXT NULL,
    raw_compensation_info JSON NULL
);

CREATE UNIQUE INDEX informers_index ON orders_tracking.informers(order_id, informer_type);

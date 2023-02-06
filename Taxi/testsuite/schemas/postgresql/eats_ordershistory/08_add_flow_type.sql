START TRANSACTION;

CREATE TYPE eats_ordershistory.flow_type_v1 AS ENUM (
    'native',
    'burger_king',
    'pickup',
    'pharmacy',
    'shop',
    'retail',
    'fuelfood',
    'fuelfood_rosneft'
    );

ALTER TABLE eats_ordershistory.orders
    ADD COLUMN flow_type eats_ordershistory.flow_type_v1;

CREATE TYPE eats_ordershistory.order_v2 AS (
    order_id TEXT,
    order_source TEXT,
    eats_user_id INTEGER,
    taxi_user_id TEXT,
    yandex_uid TEXT,
    place_id INTEGER,
    status TEXT,
    delivery_location POINT,
    total_amount TEXT,
    is_asap BOOLEAN,
    cancel_reason TEXT,
    created_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    flow_type eats_ordershistory.flow_type_v1
);

COMMIT;

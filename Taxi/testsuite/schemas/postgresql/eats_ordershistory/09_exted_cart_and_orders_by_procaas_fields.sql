START TRANSACTION;

ALTER TABLE eats_ordershistory.cart_items
    ADD COLUMN IF NOT EXISTS original_quantity INTEGER,
    ADD COLUMN IF NOT EXISTS measure_unit TEXT,
    ADD COLUMN IF NOT EXISTS parent_origin_id TEXT,
    ADD COLUMN IF NOT EXISTS cost_for_customer DECIMAL (13, 2),
    ADD COLUMN IF NOT EXISTS refunded_amount DECIMAL (13, 2),
    ADD COLUMN IF NOT EXISTS weight double precision,
    ADD COLUMN IF NOT EXISTS original_weight double precision,
    ADD COLUMN IF NOT EXISTS standalone_parent_origin_id TEXT;

CREATE TYPE eats_ordershistory.order_type_v1 AS ENUM (
    'native', 'retail', 'shop', 'lavka', 'pharmacy', 'fast_food', 'fuel_food'
    );

CREATE TYPE eats_ordershistory.shipping_type_v1 AS ENUM (
    'pickup', 'delivery'
    );

CREATE TYPE eats_ordershistory.delivery_type_v1 AS ENUM (
    'native', 'marketplace'
    );

ALTER TABLE eats_ordershistory.orders
    ADD COLUMN IF NOT EXISTS order_type eats_ordershistory.order_type_v1,
    ADD COLUMN IF NOT EXISTS original_total_amount TEXT,
    ADD COLUMN IF NOT EXISTS currency TEXT,
    ADD COLUMN IF NOT EXISTS shipping_type eats_ordershistory.shipping_type_v1,
    ADD COLUMN IF NOT EXISTS delivery_type eats_ordershistory.delivery_type_v1,
    ADD COLUMN IF NOT EXISTS last_revision_id TEXT;


CREATE TYPE eats_ordershistory.order_v3 AS (
    order_id TEXT,
    order_source TEXT,
    eats_user_id INTEGER,
    taxi_user_id TEXT,
    yandex_uid TEXT,
    place_id INTEGER,
    status text,
    delivery_location POINT,
    total_amount TEXT,
    is_asap BOOLEAN,
    cancel_reason TEXT,
    created_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    flow_type eats_ordershistory.flow_type_v1,
    order_type eats_ordershistory.order_type_v1,
    original_total_amount TEXT,
    currency TEXT,
    shipping_type eats_ordershistory.shipping_type_v1,
    delivery_type eats_ordershistory.delivery_type_v1,
    last_revision_id TEXT
);

CREATE TYPE eats_ordershistory.cart_item_v3 AS (
    order_id TEXT,
    place_menu_item_id INTEGER,
    product_id TEXT,
    name TEXT,
    quantity INTEGER,
    origin_id TEXT,
    catalog_type eats_ordershistory.catalog_type_v1,
    original_quantity INTEGER,
    measure_unit TEXT,
    parent_origin_id TEXT,
    cost_for_customer DECIMAL (13, 2),
    refunded_amount DECIMAL (13, 2),
    weight double precision,
    original_weight double precision,
    standalone_parent_origin_id TEXT
);

COMMIT;

BEGIN;

ALTER TABLE storage.places ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;
ALTER TABLE storage.delivery_zones ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;

CREATE TYPE storage.place_v3 AS (
    id BIGINT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    slug TEXT,
    enabled BOOLEAN,
    name TEXT,
    revision BIGINT,
    type storage.place_type,
    business TEXT,
    launched_at TIMESTAMPTZ,
    payment_methods storage.place_payment_method[],
    gallery storage.place_gallery[],
    brand storage.place_brand,
    address storage.place_address,
    country storage.place_country,
    categories storage.place_category[],
    quick_filters storage.place_quick_filter[],
    wizard_quick_filters storage.place_quick_filter[],
    region storage.place_region,
    location POINT,
    price_category storage.place_price_category,
    assembly_cost INTEGER,
    rating JSON,
    extra_info JSON,
    features JSON,
    timing JSON,
    sorting JSON,
    address_comment TEXT,
    contacts JSON,

    archived BOOLEAN
);

CREATE TYPE storage.delivery_zone_v2 AS (
    id BIGINT,
    place_id BIGINT,
    couriers_zone_id BIGINT,
    name TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    revision BIGINT,
    enabled BOOLEAN,
    couriers_type storage.delivery_zone_couriers_type,
    shipping_type storage.delivery_zone_shipping_type,
    delivery_conditions storage.delivery_zone_delivery_condition[],
    market_avg_time FLOAT,
    arrival_time FLOAT,
    working_intervals storage.delivery_zone_working_interval[],
    polygon POLYGON,

    archived BOOLEAN
);

COMMIT;

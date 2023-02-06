BEGIN;

-- В проде в таблицу зон идут минимум 15 RPS на запись и таймаута 1s не хватает:
SET LOCAL lock_timeout='3s';


ALTER TABLE storage.places
    ADD COLUMN hash TEXT;

-- Diff с storage.place_v5:
-- * добавили поле hash
CREATE TYPE storage.place_v6 AS (
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
    working_intervals storage.working_interval[],
    allowed_couriers_types storage.delivery_zone_couriers_type[],
    archived BOOLEAN,
    revision_id BIGINT,
    hash TEXT
);


ALTER TABLE storage.delivery_zones
    ADD COLUMN hash TEXT;

-- Diff с storage.delivery_zone_v5:
-- * добавили поле hash
CREATE TYPE storage.delivery_zone_v6 AS (
    id BIGINT,
    source storage.delivery_zone_source,
    external_id TEXT,
    place_id BIGINT,
    places_ids BIGINT[],
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
    working_intervals storage.working_interval[],
    polygons POLYGON[],
    archived BOOLEAN,
    revision_id BIGINT,
    hash TEXT
);

COMMIT;

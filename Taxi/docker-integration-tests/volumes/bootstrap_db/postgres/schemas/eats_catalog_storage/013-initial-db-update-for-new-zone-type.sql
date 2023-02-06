-- Изначальное обновление БД до выкатки кода
BEGIN;

-- Замечание: До PostgreSQL 11 добавление столбца с не-NULL значением по умолчанию надолго заблокирует таблицу,
-- поэтому мы всегда добавляем столбцы с NULL значением по умолчанию.

CREATE TYPE storage.delivery_zone_source AS ENUM ('eats_core', 'yandex_rover');

CREATE TYPE storage.working_interval AS (
    interval_from TIMESTAMPTZ,
    interval_to TIMESTAMPTZ
);

CREATE CAST (storage.working_interval AS storage.delivery_zone_working_interval)
    WITH INOUT AS IMPLICIT;

CREATE CAST (storage.delivery_zone_working_interval AS storage.working_interval)
    WITH INOUT;


ALTER TABLE storage.places
    ADD COLUMN working_intervals storage.delivery_zone_working_interval[],
    ADD COLUMN allowed_couriers_types storage.delivery_zone_couriers_type[];

-- Diff с storage.place_v4:
-- * добавили поле working_intervals
-- * добавили поле allowed_couriers_types
CREATE TYPE storage.place_v5 AS (
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

    revision_id BIGINT
);


ALTER TABLE storage.delivery_zones
    ADD COLUMN source storage.delivery_zone_source,
    ADD COLUMN source_id TEXT,
    ALTER COLUMN place_id DROP NOT NULL,
    ADD COLUMN places_ids BIGINT[],
    ADD COLUMN polygons POLYGON[];

-- Diff с storage.delivery_zone_v3:
-- * добавили поле source
-- * добавили поле source_id
-- * добавили поле places_ids
-- * изменили тип поля working_intervals (было storage.delivery_zone_working_interval[])
-- * заменили поле polygon типа POLYGON на поле polygons
CREATE TYPE storage.delivery_zone_v4 AS (
    id BIGINT,
    source storage.delivery_zone_source,
    source_id TEXT,
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

    revision_id BIGINT
);

COMMIT;

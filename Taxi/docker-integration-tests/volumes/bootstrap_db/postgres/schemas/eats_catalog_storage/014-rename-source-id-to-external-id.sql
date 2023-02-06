BEGIN;

-- В проде база долго отвечает и таймаута 1s не хватает:
SET LOCAL lock_timeout='3s';

ALTER TABLE storage.delivery_zones
    RENAME source_id TO external_id;

ALTER TABLE storage.delivery_zones
    ADD COLUMN source_id TEXT;

-- Diff с storage.delivery_zone_v4:
-- * переименовали поле source_id в external_id
CREATE TYPE storage.delivery_zone_v5 AS (
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

    revision_id BIGINT
);

COMMIT;

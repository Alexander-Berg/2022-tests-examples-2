BEGIN;

CREATE SEQUENCE IF NOT EXISTS storage.delivery_zones_revision START 1;

ALTER TABLE storage.delivery_zones
    ADD revision_id BIGINT NOT NULL DEFAULT nextval('storage.delivery_zones_revision');

CREATE TYPE storage.delivery_zone_v3 AS (
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
    archived BOOLEAN,

    revision_id BIGINT
);

COMMIT;

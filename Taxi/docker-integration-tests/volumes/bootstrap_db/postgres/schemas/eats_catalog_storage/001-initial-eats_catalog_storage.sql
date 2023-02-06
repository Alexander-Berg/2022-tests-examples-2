BEGIN;

CREATE SCHEMA storage;

CREATE TYPE storage.place_gallery AS (
    type TEXT,
    url TEXT,
    template TEXT,
    weight INTEGER
);

CREATE TYPE storage.place_brand AS (
    id BIGINT,
    slug TEXT,
    name TEXT
);

CREATE TYPE storage.place_address AS (
    city TEXT,
    short TEXT
);

CREATE TYPE storage.place_country_currency AS (
    code TEXT,
    sign TEXT
);

CREATE TYPE storage.place_country AS (
    id BIGINT,
    name TEXT,
    code TEXT,
    currency storage.place_country_currency
);

CREATE TYPE storage.place_category AS (
    id BIGINT,
    name TEXT
);

CREATE TYPE storage.place_quick_filter AS (
    id BIGINT,
    slug TEXT
);

CREATE TYPE storage.place_region AS (
    id BIGINT,
    geobase_ids BIGINT[],
    time_zone TEXT
);

CREATE TYPE storage.place_price_category AS (
    id BIGINT,
    name TEXT,
    value FLOAT
);

CREATE TYPE storage.place_type AS ENUM ('native', 'marketplace');
CREATE TYPE storage.place_payment_method AS ENUM ('cash', 'payture', 'apple_pay', 'taxi', 'google_pay');

CREATE TABLE storage.places(
    id BIGINT NOT NULL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    slug TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    name TEXT NOT NULL,
    revision BIGINT NOT NULL DEFAULT 0,
    type storage.place_type NOT NULL,
    business TEXT NOT NULL,
    launched_at TIMESTAMPTZ NOT NULL,
    payment_methods storage.place_payment_method[] NOT NULL,
    gallery storage.place_gallery[] NOT NULL,
    brand storage.place_brand NOT NULL,
    address storage.place_address NOT NULL,
    country storage.place_country NOT NULL,
    categories storage.place_category[] NOT NULL,
    quick_filters storage.place_quick_filter[] NOT NULL,
    wizard_quick_filters storage.place_quick_filter[] NOT NULL,
    region storage.place_region NOT NULL,
    location POINT NOT NULL,
    price_category storage.place_price_category NOT NULL,
    assembly_cost INTEGER NOT NULL,
    rating JSON NOT NULL,
    extra_info JSON NOT NULL,
    features JSON NOT NULL,
    timing JSON NOT NULL,
    sorting JSON NOT NULL
);

CREATE TYPE storage.delivery_zone_working_interval AS (
	interval_from TIMESTAMPTZ,
    interval_to TIMESTAMPTZ
);

CREATE TYPE storage.delivery_zone_couriers_type AS ENUM ('pedestrian', 'bicycle', 'vehicle', 'motorcycle', 'electric_bicycle', 'yandex_taxi');
CREATE TYPE storage.delivery_zone_shipping_type AS ENUM ('delivery', 'pickup');
CREATE TYPE storage.delivery_zone_delivery_condition AS (
    delivery_cost INTEGER,
	order_cost INTEGER
);

CREATE TABLE storage.delivery_zones(
    id BIGINT NOT NULL PRIMARY KEY,
    place_id BIGINT NOT NULL REFERENCES storage.places(id),
    couriers_zone_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revision BIGINT NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL,
    couriers_type storage.delivery_zone_couriers_type NOT NULL,
    shipping_type storage.delivery_zone_shipping_type NOT NULL,
    delivery_conditions storage.delivery_zone_delivery_condition[] NOT NULL,
    market_avg_time FLOAT,
    arrival_time FLOAT,
    working_intervals storage.delivery_zone_working_interval[] NOT NULL,
    polygon POLYGON
);

CREATE TABLE storage.distlocks(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE TABLE storage.distlock_periodic_updates (
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

CREATE OR REPLACE FUNCTION trigger_set_updated_at_timestamp()
	RETURNS TRIGGER AS $$
BEGIN
	NEW.updated_at = NOW();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_timestamp_places
	BEFORE UPDATE ON storage.places
	FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();

CREATE TRIGGER set_updated_at_timestamp_delivery_zones
	BEFORE UPDATE ON storage.delivery_zones
	FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();

COMMIT;


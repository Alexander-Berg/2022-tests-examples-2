BEGIN;

CREATE SEQUENCE IF NOT EXISTS storage.places_revision START 1;

ALTER TABLE storage.places
    ADD revision_id BIGINT NOT NULL DEFAULT nextval('storage.places_revision');

CREATE TYPE storage.place_v4 AS (
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
    archived BOOLEAN,

    revision_id BIGINT
);

COMMIT;

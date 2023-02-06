BEGIN;

CREATE TYPE storage.brand_picture_scale_type AS ENUM ('aspect_fit', 'aspect_fill');

-- Diff с storage.place_brand:
-- * добавлено поле `picture_scale_type`
CREATE TYPE storage.place_brand_v2 AS (
    id                  BIGINT,
    slug                TEXT,
    name                TEXT,
    picture_scale_type  storage.brand_picture_scale_type
);

CREATE FUNCTION place_brand_to_place_brand_v2 (storage.place_brand)
RETURNS storage.place_brand_v2 AS $$
SELECT (
    $1.id,
    $1.slug,
    $1.name,
    'aspect_fit'
)::storage.place_brand_v2;
$$ STRICT IMMUTABLE LANGUAGE SQL;

CREATE FUNCTION place_brand_v2_to_place_brand (storage.place_brand_v2)
RETURNS storage.place_brand AS $$
SELECT (
    $1.id,
    $1.slug,
    $1.name
)::storage.place_brand;
$$ STRICT IMMUTABLE LANGUAGE SQL;

CREATE CAST (storage.place_brand AS storage.place_brand_v2)
WITH FUNCTION place_brand_to_place_brand_v2(storage.place_brand);

CREATE CAST (storage.place_brand_v2 AS storage.place_brand)
WITH FUNCTION place_brand_v2_to_place_brand(storage.place_brand_v2) AS ASSIGNMENT;

-- Diff с storage.place_v6:
-- * поле brand теперь типа storage.place_brand_v2
CREATE TYPE storage.place_v7 AS (
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
    brand storage.place_brand_v2,
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

COMMIT;

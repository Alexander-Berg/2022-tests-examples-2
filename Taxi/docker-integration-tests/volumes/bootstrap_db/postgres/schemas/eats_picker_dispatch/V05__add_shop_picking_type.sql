BEGIN;

CREATE TYPE eats_picker_dispatch.shop_picking_type_t AS ENUM('our_picking', 'shop_picking');

ALTER TABLE eats_picker_dispatch.places ADD COLUMN IF NOT EXISTS shop_picking_type eats_picker_dispatch.shop_picking_type_t;

CREATE TYPE eats_picker_dispatch.place_v4 AS (
    id BIGINT,
    revision_id BIGINT,
    slug TEXT,
    brand_id BIGINT,
    country_id BIGINT,
    region_id BIGINT,
    time_zone TEXT,
    city TEXT,
    working_intervals eats_picker_dispatch.working_interval[],
    enabled BOOL,
    updated_at TIMESTAMPTZ,
    synchronized_at TIMESTAMPTZ,
    auto_disabled_at TIMESTAMPTZ,
    last_time_had_pickers TIMESTAMPTZ,
    shop_picking_type eats_picker_dispatch.shop_picking_type_t
    );

COMMIT;

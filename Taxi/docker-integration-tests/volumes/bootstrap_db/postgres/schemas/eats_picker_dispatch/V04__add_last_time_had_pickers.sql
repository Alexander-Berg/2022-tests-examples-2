BEGIN;

ALTER TABLE eats_picker_dispatch.places ADD COLUMN IF NOT EXISTS last_time_had_pickers TIMESTAMPTZ;

CREATE TYPE eats_picker_dispatch.place_v3 AS (
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
    last_time_had_pickers TIMESTAMPTZ
);

COMMIT;

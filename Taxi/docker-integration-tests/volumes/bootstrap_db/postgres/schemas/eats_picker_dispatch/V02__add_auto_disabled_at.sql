BEGIN;

ALTER TABLE eats_picker_dispatch.places ADD COLUMN IF NOT EXISTS auto_disabled_at TIMESTAMPTZ;

CREATE TYPE eats_picker_dispatch.place_v2 AS (
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
    auto_disabled_at TIMESTAMPTZ
);

COMMIT;

BEGIN;

CREATE TYPE fts_indexer.place_state_meta_v6 AS (
    place_id BIGINT,
    place_slug TEXT,
    brand_id BIGINT,
    enabled BOOLEAN,
    business fts_indexer.business_type_v1
);

COMMIT;

ALTER TABLE fts.place ADD COLUMN IF NOT EXISTS business fts_indexer.business_type_v1 DEFAULT 'shop';

CREATE TYPE fts.place_v2 AS (
    place_id BIGINT,
    brand_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN,
    business fts_indexer.business_type_v1
);

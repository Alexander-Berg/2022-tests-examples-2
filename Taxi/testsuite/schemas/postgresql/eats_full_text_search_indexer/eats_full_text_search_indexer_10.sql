BEGIN TRANSACTION;

CREATE TYPE fts_indexer.business_type_v1 AS enum ('restaurant', 'store', 'shop', 'pharmacy', 'zapravki');

ALTER TABLE fts_indexer.place_state
    ADD COLUMN IF NOT EXISTS business fts_indexer.business_type_v1;

CREATE TYPE fts_indexer.place_state_meta_v3 AS (
    place_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN,
    market_feed_id BIGINT,
    market_partner_id BIGINT,
    market_business_id BIGINT,
    business fts_indexer.business_type_v1
);

COMMIT TRANSACTION;

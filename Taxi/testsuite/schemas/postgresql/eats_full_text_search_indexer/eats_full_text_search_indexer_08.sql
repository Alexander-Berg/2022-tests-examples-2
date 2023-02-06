BEGIN TRANSACTION;

ALTER TABLE fts_indexer.place_state
    ADD COLUMN IF NOT EXISTS market_feed_id BIGINT,
    ADD COLUMN IF NOT EXISTS market_partner_id BIGINT,
    ADD COLUMN IF NOT EXISTS market_business_id BIGINT;

CREATE TYPE fts_indexer.place_state_meta_v2 AS (
    place_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN,
    market_feed_id BIGINT,
    market_partner_id BIGINT,
    market_business_id BIGINT
);

COMMIT TRANSACTION;

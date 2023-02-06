BEGIN TRANSACTION;

ALTER TABLE fts_indexer.place_state
    ADD COLUMN IF NOT EXISTS nomenclature_market_feed_id BIGINT,
    ADD COLUMN IF NOT EXISTS nomenclature_market_partner_id BIGINT,
    ADD COLUMN IF NOT EXISTS nomenclature_market_business_id BIGINT;

CREATE TYPE fts_indexer.place_state_meta_v4 AS (
    place_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN,
    market_feed_id BIGINT,
    market_partner_id BIGINT,
    market_business_id BIGINT,
    nomenclature_market_feed_id BIGINT,
    nomenclature_market_partner_id BIGINT,
    nomenclature_market_business_id BIGINT,
    business fts_indexer.business_type_v1
);

COMMIT TRANSACTION;

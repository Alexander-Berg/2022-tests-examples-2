BEGIN TRANSACTION;

DROP SCHEMA IF EXISTS fts_indexer CASCADE;

CREATE SCHEMA IF NOT EXISTS fts_indexer;

CREATE TYPE fts_indexer.business_type_v1 AS enum ('restaurant', 'store', 'shop', 'pharmacy', 'zapravki');

CREATE TABLE IF NOT EXISTS fts_indexer.place_state (
    place_id BIGINT PRIMARY KEY,
    place_slug TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    etag TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    business fts_indexer.business_type_v1,
    market_feed_id BIGINT,
    market_partner_id BIGINT,
    market_business_id BIGINT,
    nomenclature_market_feed_id BIGINT,
    nomenclature_market_partner_id BIGINT,
    nomenclature_market_business_id BIGINT
);

CREATE INDEX IF NOT EXISTS idx__place_state__updated_at ON fts_indexer.place_state(updated_at);

COMMIT TRANSACTION;

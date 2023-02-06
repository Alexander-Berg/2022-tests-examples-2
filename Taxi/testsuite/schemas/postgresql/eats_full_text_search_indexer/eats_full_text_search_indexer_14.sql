BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.retail_document_meta (
  prefix INTEGER NOT NULL,                        -- prefix (kps) в saas
  url TEXT NOT NULL,                              -- url документа (идентификатор в saas)
  hash TEXT NOT NULL,                             -- hash документа
  place_slug TEXT NOT NULL,                       -- id заведения
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- время обновления
  PRIMARY KEY (prefix, url)
);

CREATE INDEX idx__retail_document_meta__prefix__place_slug ON fts_indexer.retail_document_meta(prefix, place_slug);

ALTER TABLE fts_indexer.place_state ADD COLUMN IF NOT EXISTS brand_id BIGINT;

CREATE TYPE fts_indexer.place_state_meta_v5 AS (
    place_id BIGINT,
    place_slug TEXT,
    brand_id BIGINT,
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

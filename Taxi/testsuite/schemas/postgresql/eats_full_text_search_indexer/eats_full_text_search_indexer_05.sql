BEGIN TRANSACTION;

ALTER TABLE fts_indexer.place_state ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx__place_state__updated_at ON fts_indexer.place_state(updated_at);

CREATE TYPE fts_indexer.document_meta_key_v1 AS (
  prefix INTEGER,
  place_slug TEXT,
  url TEXT
);

CREATE TABLE IF NOT EXISTS fts_indexer.update_retail_place_state (
    id SMALLINT PRIMARY KEY,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts_indexer.update_retail_place_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT TRANSACTION;

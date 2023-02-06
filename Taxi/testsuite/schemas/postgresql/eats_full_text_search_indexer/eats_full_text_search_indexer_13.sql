BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.update_product_scores_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts_indexer.update_product_scores_state (
    id SMALLINT PRIMARY KEY,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts_indexer.product_scores_last_revision (
    table_path TEXT UNIQUE NOT NULL,
    revision BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fts_indexer.product_scores (
    brand_id BIGINT NOT NULL,
    origin_id TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux__product_scores__brand_id__origin_id ON fts_indexer.product_scores(brand_id, origin_id);

CREATE TYPE fts_indexer.product_score_v1 AS (
    brand_id BIGINT,
    origin_id TEXT,
    score DOUBLE PRECISION
);

COMMIT TRANSACTION;

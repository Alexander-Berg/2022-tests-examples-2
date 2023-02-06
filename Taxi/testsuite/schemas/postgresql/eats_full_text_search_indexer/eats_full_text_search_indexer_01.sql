BEGIN TRANSACTION;

CREATE SCHEMA IF NOT EXISTS fts_indexer;

CREATE TABLE IF NOT EXISTS fts_indexer.place_state (
    place_id BIGINT PRIMARY KEY,        -- заполняется каталогом
    place_slug TEXT NOT NULL,           -- заполняется каталогом
    enabled BOOLEAN NOT NULL,           -- заполняется каталогом
    etag TEXT                           -- заполняется продуктами
);

CREATE TABLE IF NOT EXISTS fts_indexer.catalog_state (
    id SMALLINT PRIMARY KEY,             -- ключ
    updated_at TIMESTAMPTZ,              -- время самого свежего ресторана из каталога
    last_incremental_update TIMESTAMPTZ, -- время когда началась последняя итерация обхода каталога
    last_full_update TIMESTAMPTZ         -- время когда началась последняя полная итерация обхода каталога
);

CREATE TYPE fts_indexer.place_state_meta_v1 AS (
    place_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN
);

CREATE TYPE fts_indexer.place_state_data_v1 AS (
    place_id BIGINT,
    place_slug TEXT,
    etag TEXT
);

CREATE TABLE IF NOT EXISTS fts_indexer.catalog_storage_periodic_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT TRANSACTION;

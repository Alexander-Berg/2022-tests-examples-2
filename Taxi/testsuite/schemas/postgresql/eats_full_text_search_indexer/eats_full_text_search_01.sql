BEGIN TRANSACTION;

DROP SCHEMA IF EXISTS fts CASCADE; -- !!!!!!!!!

CREATE SCHEMA IF NOT EXISTS fts;

CREATE TABLE IF NOT EXISTS fts.place_update_state (
    id SMALLINT PRIMARY KEY,             -- ключ
    updated_at TIMESTAMPTZ,              -- время самого свежего ресторана из каталога
    last_incremental_update TIMESTAMPTZ, -- время когда началась последняя итерация обхода каталога
    last_full_update TIMESTAMPTZ         -- время когда началась последняя полная итерация обхода каталога
);

CREATE TABLE IF NOT EXISTS fts.mapping_state (
    id SMALLINT PRIMARY KEY,             -- ключ
    updated_at TIMESTAMPTZ               -- последнего завершенного обновления
);

CREATE TABLE IF NOT EXISTS fts.place (
    place_id BIGINT PRIMARY KEY,                   -- Идентификатор заведения
    brand_id BIGINT,                               -- Идентификатор бренда заведения
    place_slug TEXT NOT NULL,                      -- Строковый идентификатор заведения
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время обновления заведения
    enabled BOOLEAN                                -- Признак включенности
);

CREATE INDEX idx__place__updated_at ON fts.place(updated_at);

CREATE TABLE IF NOT EXISTS fts.brand (
    brand_id BIGINT PRIMARY KEY,                   -- Идентификатор бренда заведения
    picture_scale TEXT,                            -- Формат скейлинга картинки товаров бренда
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  -- Время обновления бренда
);

CREATE INDEX idx__brand__updated_at ON fts.brand(updated_at);

CREATE TABLE IF NOT EXISTS fts.categories_mapping (
    place_id BIGINT NOT NULL,                      -- Идентификатор заведения
    core_id BIGINT NOT NULL,                       -- Идентификатор категории в коре
    core_parent_id BIGINT,                         -- Идентификатор родительской категории в коре
    origin_id TEXT NOT NULL,                       -- Идентификатор категории в системе партнера
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время одновления маппинга
    PRIMARY KEY(place_id, core_id)
);

CREATE INDEX idx__categories_mapping__updated_at ON fts.categories_mapping(updated_at);

CREATE TABLE IF NOT EXISTS fts.items_mapping (
    place_id BIGINT NOT NULL,                      -- Идентификатор заведения
    core_id BIGINT NOT NULL,                       -- Идентификатор товара в коре
    core_parent_category_id BIGINT,                -- Идентификатор родительской категории товара
    origin_id TEXT NOT NULL,                       -- Идентификатор товара в системе партнера
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время обновления маппинга
    PRIMARY KEY (place_id, core_id)
);

CREATE INDEX idx__items_mapping__updated_at ON fts.items_mapping(updated_at);

CREATE TYPE fts.place_v1 AS (
    place_id BIGINT,
    brand_id BIGINT,
    place_slug TEXT,
    enabled BOOLEAN
);

CREATE TYPE fts.brand_v1 AS (
    brand_id BIGINT,
    picture_scale TEXT 
);

CREATE TYPE fts.categories_mapping_v1 AS (
    place_id BIGINT,
    core_id BIGINT,
    core_parent_id BIGINT,
    origin_id TEXT
);

CREATE TYPE fts.items_mapping_v1 AS (
    place_id BIGINT,
    core_id BIGINT,
    core_parent_category_id BIGINT,
    origin_id TEXT
);

CREATE TABLE IF NOT EXISTS fts.place_update_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts.mapping_periodic_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT TRANSACTION;

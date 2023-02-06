BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts.selector_statistics (
    query TEXT PRIMARY KEY, -- текст поискового запроса
    count BIGINT NOT NULL, -- число запросов
    restaurant_percentage SMALLINT NOT NULL, -- вероятность перехода в ресторан
    shop_percentage SMALLINT NOT NULL, -- вероятность перехода в магазин
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fts.selector_statistics_last_revision (
    table_path TEXT UNIQUE NOT NULL,
    revision BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fts.distlocks (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts.distlock_periodic_updates
(
    task_id TEXT PRIMARY KEY,
    updated TIMESTAMPTZ NOT NULL
);

CREATE TYPE fts.selector_statistics_v1 AS (
    query TEXT,
    count BIGINT,
    restaurant_percentage SMALLINT,
    shop_percentage SMALLINT
);

COMMIT TRANSACTION;

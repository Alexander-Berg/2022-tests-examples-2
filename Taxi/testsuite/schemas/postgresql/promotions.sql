SET default_text_search_config = 'pg_catalog.russian';

CREATE SCHEMA IF NOT EXISTS promotions;

CREATE TABLE promotions.yql_cache(
    promotion_id TEXT NOT NULL,
    yandex_uid TEXT,
    user_id TEXT,
    phone_id TEXT,
    data jsonb NOT NULL
);

SET default_text_search_config = 'pg_catalog.russian';

CREATE SCHEMA IF NOT EXISTS inapp_communications;

CREATE TABLE inapp_communications.promos_on_map_cache(
    yandex_uid TEXT NOT NULL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    longitude DOUBLE PRECISION  NOT NULL,
    latitude DOUBLE PRECISION  NOT NULL,
    promos_on_map jsonb NOT NULL
);

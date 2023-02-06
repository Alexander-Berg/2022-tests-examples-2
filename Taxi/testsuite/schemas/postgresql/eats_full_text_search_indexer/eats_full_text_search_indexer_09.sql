BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.restaurant_menu_state (
    id SMALLINT PRIMARY KEY,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS fts_indexer.restaurant_menu_periodic_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT TRANSACTION;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.products_periodic_distlock (
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT TRANSACTION;

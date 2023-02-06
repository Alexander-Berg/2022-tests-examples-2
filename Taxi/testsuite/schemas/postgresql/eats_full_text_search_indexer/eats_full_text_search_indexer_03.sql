BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.products_state (
    id SMALLINT PRIMARY KEY,  -- ключ
    last_update TIMESTAMPTZ   -- время начала последней завершенной итерации
);

COMMIT TRANSACTION;

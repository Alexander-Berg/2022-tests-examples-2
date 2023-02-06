BEGIN TRANSACTION;

DROP INDEX IF EXISTS fts_indexer.idx__document_meta__updated_at;

COMMIT TRANSACTION;
